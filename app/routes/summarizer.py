from fastapi import APIRouter, Depends, HTTPException, Query
from app.utils.auth_dependency import get_current_user
from app.services.db_service import get_db_connection
from app.services.summarizer_service import generate_summary

router = APIRouter(prefix="/summaries", tags=["Summaries"])

@router.get("/latest/{doc_id}")
def get_latest_summary(doc_id: int, user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT s.id, s.summary, s.created_at "
            "FROM summaries s JOIN documents d ON s.document_id = d.id "
            "WHERE s.document_id = %s AND d.user_id = %s "
            "ORDER BY s.created_at DESC, s.id DESC LIMIT 1",
            (doc_id, user["id"]),
        )
        row = cur.fetchone()
        cur.close(); conn.close()

        if not row:
            return {"summary": None, "cached": False}

        return {
            "summary_id": row[0],
            "summary": row[1],
            "created_at": row[2],
            "cached": True
        }
    except Exception as e:
        print("Get latest summary error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doc_id}")
def list_summaries(doc_id: int, user: dict = Depends(get_current_user)):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT s.id, s.summary, s.created_at "
            "FROM summaries s JOIN documents d ON s.document_id = d.id "
            "WHERE s.document_id = %s AND d.user_id = %s "
            "ORDER BY s.created_at DESC, s.id DESC",
            (doc_id, user["id"]),
        )
        rows = cur.fetchall()
        cur.close(); conn.close()

        items = [{"summary_id": r[0], "summary": r[1], "created_at": r[2]} for r in rows]
        return {"items": items}
    except Exception as e:
        print("List summaries error:", e)
        raise HTTPException(status_code=500, detail=str(e))

# Keep summarize under POST, but short-circuit unless force=true
@router.post("/generate/{doc_id}")
def summarize_document(doc_id: int, user: dict = Depends(get_current_user), force: bool = Query(False)):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check ownership and get content
        cur.execute("SELECT id, content FROM documents WHERE id = %s AND user_id = %s", (doc_id, user["id"]))
        doc = cur.fetchone()
        if not doc:
            cur.close(); conn.close()
            raise HTTPException(status_code=404, detail="Document not found or not yours")
        text = doc[1]
        if not text or not text.strip():
            cur.close(); conn.close()
            raise HTTPException(status_code=400, detail="No content found in document")

        # If not forcing, try cache
        if not force:
            cur.execute(
                "SELECT id, summary, created_at FROM summaries WHERE document_id = %s ORDER BY created_at DESC, id DESC LIMIT 1",
                (doc_id,),
            )
            row = cur.fetchone()
            if row:
                cur.close(); conn.close()
                return {
                    "summary_id": row[0],
                    "summary": row[1],
                    "created_at": row[2],
                    "cached": True
                }

        # Generate with AI
        summary = generate_summary(text)

        # Store
        cur.execute("INSERT INTO summaries (document_id, summary) VALUES (%s, %s) RETURNING id", (doc_id, summary))
        s_id = cur.fetchone()[0]
        conn.commit()
        cur.close(); conn.close()

        return {
            "message": "Summary generated successfully",
            "summary_id": s_id,
            "document_id": doc_id,
            "summary": summary,
            "cached": False
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Summarization Error:", e)
        raise HTTPException(status_code=500, detail=str(e))