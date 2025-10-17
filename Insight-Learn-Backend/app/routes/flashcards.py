from fastapi import APIRouter, Depends, HTTPException, Query
from app.utils.auth_dependency import get_current_user
from app.services.db_service import get_db_connection
from app.services.flashcard_service import generate_flashcards

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])

@router.post("/{doc_id}")
def create_flashcards(
    doc_id: int,
    user: dict = Depends(get_current_user),
    num_cards: int = Query(5, ge=1, le=20),
    force: bool = Query(False),
):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Verify doc belongs to user
        cur.execute("SELECT id, content FROM documents WHERE id = %s AND user_id = %s", (doc_id, user["id"]))
        doc = cur.fetchone()
        if not doc:
            cur.close(); conn.close()
            raise HTTPException(status_code=404, detail="Document not found or not yours")

        text = doc[1]
        if not text or not text.strip():
            cur.close(); conn.close()
            raise HTTPException(status_code=400, detail="No content found in document")

        # If not forcing, return cached flashcards if any exist
        if not force:
            cur.execute(
                "SELECT id, question, answer, created_at FROM flashcards WHERE document_id = %s ORDER BY created_at DESC",
                (doc_id,)
            )
            rows = cur.fetchall()
            if rows:
                cur.close(); conn.close()
                cards = [
                    {"id": r[0], "question": r[1], "answer": r[2], "created_at": r[3]}
                    for r in rows
                ]
                return {
                    "message": f"Using existing {len(cards)} flashcards",
                    "flashcards": cards,
                    "cached": True
                }

        # Generate
        cards = generate_flashcards(text, num_cards=num_cards)
        if not cards:
            cur.close(); conn.close()
            raise HTTPException(status_code=502, detail="Model returned no usable flashcards")

        ids = []
        for fc in cards:
            cur.execute(
                "INSERT INTO flashcards (document_id, question, answer) VALUES (%s, %s, %s) RETURNING id",
                (doc_id, fc["question"], fc["answer"])
            )
            ids.append(cur.fetchone()[0])

        conn.commit()
        # Fetch full list to return with timestamps
        cur.execute(
            "SELECT id, question, answer, created_at FROM flashcards WHERE document_id = %s ORDER BY created_at DESC",
            (doc_id,)
        )
        rows = cur.fetchall()
        cur.close(); conn.close()

        cards_full = [
            {"id": r[0], "question": r[1], "answer": r[2], "created_at": r[3]}
            for r in rows
        ]

        return {
            "message": f"{len(ids)} flashcards created successfully",
            "flashcard_ids": ids,
            "flashcards": cards_full,
            "cached": False
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Flashcards Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list/{doc_id}")
def get_flashcards(doc_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()

    # Verify doc belongs to user
    cur.execute("SELECT id FROM documents WHERE id = %s AND user_id = %s", (doc_id, user["id"]))
    doc = cur.fetchone()
    if not doc:
        cur.close(); conn.close()
        raise HTTPException(status_code=404, detail="Document not found or not yours")

    # Fetch flashcards
    cur.execute(
        "SELECT id, question, answer, created_at FROM flashcards WHERE document_id = %s",
        (doc_id,)
    )
    rows = cur.fetchall()
    cur.close(); conn.close()

    flashcards = [
        {"id": row[0], "question": row[1], "answer": row[2], "created_at": row[3]}
        for row in rows
    ]

    return {
        "document_id": doc_id,
        "total_flashcards": len(flashcards),
        "flashcards": flashcards
    }