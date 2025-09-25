import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_flashcards(text: str, num_cards: int = 5) -> list[dict]:
    prompt = f"""
    Create {num_cards} educational flashcards (question-answer pairs) 
    based on the following text. 
    Respond ONLY with a valid JSON list of objects in this format:
    [
      {{"question": "What is ...?", "answer": "It is ..."}},
      {{"question": "...", "answer": "..."}}
    ]

    Text: {text}
    """

    response = model.generate_content(prompt)

    try:
        raw_output = response.text.strip()
        start = raw_output.find("[")
        end = raw_output.rfind("]") + 1
        json_str = raw_output[start:end]

        flashcards = json.loads(json_str)
        return flashcards
    except Exception as e:
        print("Flashcard Parse Error:", e)
        print("Raw Gemini output:", response.text[:500])
        return []
