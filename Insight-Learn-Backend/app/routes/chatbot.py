from fastapi import APIRouter, Depends, HTTPException, Query
from app.utils.auth_dependency import get_current_user
from app.services.embedding_service import model
from app.services.faiss_service import load_faiss_index
from app.services.gemini_service import ask_gemini  # or generate_text, depending on your service
from app.services.conversation_service import save_message, get_conversation_history, clear_conversation
import numpy as np

router = APIRouter(prefix="/chat", tags=["Chatbot"])

@router.get("/history/{doc_id}")
def get_chat_history(
    doc_id: int,
    user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=200),
):
    try:
        history = get_conversation_history(user["id"], doc_id, limit=limit)
        # Convert [(role, message), ...] → [{role, text}, ...]
        messages = [{"role": role, "text": msg} for role, msg in history]
        return {"document_id": doc_id, "messages": messages}
    except Exception as e:
        print("Get Chat History Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{doc_id}")
def chat_with_document(doc_id: int, query: str, user: dict = Depends(get_current_user)):
    try:
        index, chunks = load_faiss_index(doc_id)

        history = get_conversation_history(user["id"], doc_id, limit=5)
        formatted_history = "\n".join([f"{role}: {msg}" for role, msg in history])

        query_embedding = model.encode([query], normalize_embeddings=True).astype("float32")
        D, I = index.search(query_embedding, k=3)

        context = "\n\n".join([chunks[i] for i in I[0] if i < len(chunks)])
        if not context:
            raise HTTPException(status_code=400, detail="No context found for this query")

        prompt = f"""
        You are a helpful learning assistant.
        Use the provided context and conversation history to answer naturally and accurately.

        Context:
        {context}

        Previous conversation:
        {formatted_history}

        User: {query}
        Assistant:
        """.strip()

        # If no history, a simpler prompt also works
        answer = ask_gemini(context, query) if not formatted_history else ask_gemini(prompt, "")

        save_message(user["id"], doc_id, "user", query)
        save_message(user["id"], doc_id, "assistant", answer)

        return {
            "query": query,
            "context_preview": context[:500] + "...",
            "answer": answer
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No FAISS index found. Please re-upload this document.")
    except Exception as e:
        print("Chatbot Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear/{doc_id}")
def clear_chat_history(doc_id: int, user: dict = Depends(get_current_user)):
    try:
        clear_conversation(user["id"], doc_id)
        return {"message": f"Chat history cleared for document {doc_id}"}
    except Exception as e:
        print("Clear Chat Error:", e)
        raise HTTPException(status_code=500, detail=str(e))