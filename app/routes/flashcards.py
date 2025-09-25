from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth_dependency import get_current_user
from app.services.db_service import get_db_connection
from app.services.flashcard_service import generate_flashcards

router = APIRouter(prefix="/flashcards", tags=["Flashcards"])

@router.post("/{doc_id}")
def create_flashcards(doc_id: int, user: dict = Depends(get_current_user), num_cards: int = 5):
    con = get_db_connection()
    cur = con.cursor()

    cur.execute("SELECT id, content FROM documents WHERE id = %s and user_id = %s", (doc_id, user["id"]))
    doc = cur.fetchone()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    text = doc[1]
    if not text:
        raise HTTPException(status_code=400, detail="Content not found")
    
    flashcards = generate_flashcards(text,num_cards)
    if not flashcards:
        raise HTTPException(status_code=500, detail="Failsed to generate flashcard")
    
    ids = []
    for fc in flashcards:
        cur.execute("INSERT INTO flashcards (document_id, question, answer) VALUES (%s,%s,%s) RETURNING id",
                    (doc_id, fc["question"], fc["answer"]))
        ids.append(cur.fetchone()[0])

    con.commit()
    cur.close()
    con.close()

    return{
        "message": f"{len(flashcards)} flashcards created successfully",
        "flashcard_ids": ids,
        "flashcards": flashcards
    }