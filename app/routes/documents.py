import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.utils.auth_dependency import get_current_user
from app.services.db_service import get_db_connection
from app.services.pdf_service import extract_text_from_pdf
from app.services.chunk_service import chunk_text
from app.services.embedding_service import embed_text  # or embed_texts if you use that
from app.services.faiss_service import save_faiss_index
from app.services.text_utils import clean_text

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
def upload_document(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Save to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        # Extract and sanitize text
        raw_text = extract_text_from_pdf(tmp_path)
        os.remove(tmp_path)

        text = clean_text(raw_text or "")

        if not text:
            raise HTTPException(status_code=400, detail="No extractable text found in PDF")

        # Store in DB
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

        # Build FAISS index (use sanitized text)
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