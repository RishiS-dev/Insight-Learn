import os
import faiss
import numpy as np
import pickle

BASE_INDEX_DIR = "vector_indices"

def save_faiss_index(doc_id: int, embeddings, chunks):
    os.makedirs(BASE_INDEX_DIR, exist_ok=True)
    index_path = os.path.join(BASE_INDEX_DIR, f"{doc_id}.index")
    meta_path = os.path.join(BASE_INDEX_DIR, f"{doc_id}_meta.pkl")

    embeddings = np.array(embeddings).astype('float32')

    index = faiss.IndexFlatIP(embeddings.shape[1])  # cosine similarity
    index.add(embeddings)
    faiss.write_index(index, index_path)

    with open(meta_path, "wb") as f:
        pickle.dump(chunks, f)

def load_faiss_index(doc_id: int):
    index_path = os.path.join(BASE_INDEX_DIR, f"{doc_id}.index")
    meta_path = os.path.join(BASE_INDEX_DIR, f"{doc_id}_meta.pkl")

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Index or metadata file not found.")
    
    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        chunks = pickle.load(f)

    return index, chunks

def delete_faiss_index(doc_id: int):
    """
    Delete FAISS index and metadata files for the given document.
    """
    index_path = os.path.join(BASE_INDEX_DIR, f"{doc_id}.index")
    meta_path = os.path.join(BASE_INDEX_DIR, f"{doc_id}_meta.pkl")

    try:
        if os.path.exists(index_path):
            os.remove(index_path)
    except Exception:
        # ignore file errors; DB delete should still proceed
        pass

    try:
        if os.path.exists(meta_path):
            os.remove(meta_path)
    except Exception:
        pass