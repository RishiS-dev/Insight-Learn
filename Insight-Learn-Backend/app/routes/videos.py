import json
import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from app.utils.auth_dependency import get_current_user
from app.services.db_service import get_db_connection
from app.services.keyword_service import extract_keywords
from app.services.youtube_service import search_youtube, merge_dedup, youtube_enabled

router = APIRouter(prefix="/videos", tags=["Videos"])

TTL_HOURS = int(os.getenv("VIDEO_SUGGESTIONS_TTL_HOURS", "24"))

def _now():
    return datetime.now(timezone.utc)

@router.get("/{doc_id}")
def get_related_videos(
    doc_id: int,
    user: dict = Depends(get_current_user),
    limit: int = Query(6, ge=1, le=12),
    force: bool = Query(False)
):
    if not youtube_enabled():
        raise HTTPException(status_code=501, detail="YouTube integration not configured (missing API key).")

    conn = get_db_connection()
    cur = conn.cursor()

    # Ownership check and fetch title
    cur.execute("SELECT id, title FROM documents WHERE id = %s AND user_id = %s", (doc_id, user["id"]))
    doc = cur.fetchone()
    if not doc:
        cur.close(); conn.close()
        raise HTTPException(status_code=404, detail="Document not found or not yours")
    title = doc[1] or ""

    # Try cached
    if not force:
        cur.execute("SELECT items, created_at FROM video_suggestions WHERE document_id = %s", (doc_id,))
        row = cur.fetchone()
        if row:
            items_json, created_at = row
            if created_at and (created_at >= _now() - timedelta(hours=TTL_HOURS)):
                cur.close(); conn.close()
                items = items_json if isinstance(items_json, list) else json.loads(items_json)
                return {
                    "document_id": doc_id,
                    "cached": True,
                    "updated_at": created_at,
                    "videos": items[:limit]
                }

    # Fetch latest summary to guide search (fallback to title if no summary)
    cur.execute(
        "SELECT summary FROM summaries WHERE document_id = %s ORDER BY created_at DESC, id DESC LIMIT 1",
        (doc_id,)
    )
    row = cur.fetchone()
    summary_text = (row[0] if row else "") or title

    # Build search queries
    kws = extract_keywords(summary_text, top_k=8)
    q1 = " ".join(kws[:5]) if kws else title
    q2 = (title + " " + " ".join(kws[:3])).strip()[:120]
    q3 = (kws[0] + " tutorial") if kws else (title + " tutorial")
    queries = [q for q in [q1, q2, q3] if q]

    # Query YouTube and merge
    result_lists = []
    for q in queries:
        try:
            result_lists.append(search_youtube(q, max_results=max(3, limit)))
        except Exception:
            # Skip failing queries; continue
            continue
    videos = merge_dedup(result_lists)[:limit]

    # Upsert cache
    cur.execute(
        """
        INSERT INTO video_suggestions (document_id, items)
        VALUES (%s, %s)
        ON CONFLICT (document_id)
        DO UPDATE SET items = EXCLUDED.items, created_at = NOW()
        """,
        (doc_id, json.dumps(videos))
    )
    conn.commit()
    cur.close(); conn.close()

    return {
        "document_id": doc_id,
        "cached": False,
        "updated_at": _now(),
        "videos": videos
    }