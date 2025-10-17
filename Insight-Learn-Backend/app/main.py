from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, documents, summarizer, flashcards, chatbot, videos

app = FastAPI(title="InsightLearn API")

# Allow local frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(summarizer.router)
app.include_router(flashcards.router)
app.include_router(chatbot.router)
app.include_router(videos.router) 

@app.get("/")
def root():
    return {"message": "InsightLearn Backend is running"}