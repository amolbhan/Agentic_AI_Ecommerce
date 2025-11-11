import os
import pickle
import numpy as np
from backend.rag.rag_config import FAISS_DB_DIR, EMBED_DIM
from backend.rag.embedder import embed_texts

try:
    import faiss
except ImportError:
    raise ImportError("FAISS not installed. Run: pip install faiss-cpu")

_index = None
_metadata = None

def load_faiss_index():
    global _index, _metadata
    if _index is not None:
        return _index, _metadata
    index_path = os.path.join(FAISS_DB_DIR, "index.faiss")
    metadata_path = os.path.join(FAISS_DB_DIR, "metadata.pkl")
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"FAISS index not found at {index_path}. Run: python -m backend.rag.ingest")
    _index = faiss.read_index(index_path)
    with open(metadata_path, "rb") as f:
        _metadata = pickle.load(f)
    return _index, _metadata

def retrieve_relevant_chunks(query, top_k=4):
    try:
        index, metadata = load_faiss_index()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return []
    query_embedding = embed_texts([query])[0].astype('float32')
    query_embedding = np.array([query_embedding])
    distances, indices = index.search(query_embedding, top_k)
    hits = []
    texts = metadata["texts"]
    metadatas = metadata["metadatas"]
    for i, idx in enumerate(indices[0]):
        if idx < len(texts):
            hits.append({
                "id": f"doc_{idx}",
                "chunk": texts[idx],
                "distance": float(distances[0][i]),
                "source": metadatas[idx].get("source", "Unknown")
            })
    return hits
