from fastapi import FastAPI
from app.routes import auth, documents, summarizer, flashcards

app = FastAPI(title="InsightLearn API")

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(summarizer.router)
app.include_router(flashcards.router)
@app.get("/")
def root():
    return {"message": "InsightLearn Backend is running"}