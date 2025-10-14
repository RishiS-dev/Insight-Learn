import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.utils.auth_dependency import get_current_user
from app.services.db_service import get_db_connection
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import chunk_text
from app.services.embedding_service import embed_text  # or embed_texts if that's your function
from app.services.faiss_service import save_faiss_index, delete_faiss_index
from app.services.text_utils import clean_text  # NEW: sanitize extracted text

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
def upload_document(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        # Extract text and cleanup
        raw_text = extract_text_from_pdf(tmp_path)
        os.remove(tmp_path)

        # Sanitize to remove NUL/control chars and fix common UTF-16-like patterns
        text = clean_text(raw_text or "")

        if not text:
            raise HTTPException(status_code=400, detail="No extractable text found in PDF")

        # Store document in DB
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO documents (user_id, title, content) VALUES (%s, %s, %s) RETURNING id",
            (user["id"], file.filename, text),
        )
        doc_id = cur.fetchone()[0]
        con.commit()
        cur.close()
        con.close()

        # Build FAISS index for chatbot (use sanitized text)
        chunks = chunk_text(text)
        if chunks:
            embeddings = embed_text(chunks)  # or embed_texts(chunks)
            save_faiss_index(doc_id, embeddings, chunks)

        return {
            "message": "Document uploaded successfully & indexed successfully",
            "document_id": doc_id,
            "title": file.filename,
            "number_of_chunks": len(chunks),
            "preview": (text[:300] + "...") if len(text) > 300 else text
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Upload Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
def list_documents(user: dict = Depends(get_current_user)):
    try:
        con = get_db_connection()
        cur = con.cursor()
        cur.execute(
            "SELECT id, title FROM documents WHERE user_id = %s ORDER BY id DESC",
            (user["id"],),
        )
        rows = cur.fetchall()
        cur.close()
        con.close()

        docs = [{"id": r[0], "title": r[1]} for r in rows]
        return {"documents": docs}
    except Exception as e:
        print("List Documents Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{doc_id}")
def delete_document(doc_id: int, user: dict = Depends(get_current_user)):
    """
    Delete a document owned by the current user, plus its FAISS index files.
    Requires ON DELETE CASCADE on dependent tables (summaries, flashcards, conversations).
    """
    try:
        con = get_db_connection()
        cur = con.cursor()

        # Verify ownership
        cur.execute("SELECT id FROM documents WHERE id = %s AND user_id = %s", (doc_id, user["id"]))
        row = cur.fetchone()
        if not row:
            cur.close(); con.close()
            raise HTTPException(status_code=404, detail="Document not found or not yours")

        # Delete FAISS files (safe even if missing)
        delete_faiss_index(doc_id)

        # Delete the document row
        cur.execute("DELETE FROM documents WHERE id = %s AND user_id = %s", (doc_id, user["id"]))
        con.commit()
        cur.close(); con.close()

        return {"message": f"Document {doc_id} deleted", "document_id": doc_id}
    except HTTPException:
        raise
    except Exception as e:
        print("Delete Document Error:", e)
        raise HTTPException(status_code=500, detail=str(e))