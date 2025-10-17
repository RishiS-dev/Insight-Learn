from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(chunks: list[str]):
    return model.encode(chunks, normalize_embeddings=True)