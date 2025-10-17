import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_gemini(context: str, question: str) -> str:
    prompt = f"""
    Use the provided context to answer the question accurately.
    If the answer isn't found in the context, say "The document doesn't provide enough information."

    Context:
    {context}

    Question:
    {question}
    """

    response = model.generate_content(prompt)
    return response.text.strip()
