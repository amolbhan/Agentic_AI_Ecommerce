from sentence_transformers import SentenceTransformer
import numpy as np

def build_catalog_vectors(catalog, embed_model):
    """
    Precompute catalog description embeddings for semantic search.
    Returns: ids, vectors, product_map
    """
    products = catalog.get("products", [])
    descriptions = [p.get("description", "") for p in products]
    ids = [p.get("id", i) for i, p in enumerate(products)]
    vectors = embed_model.encode(descriptions, show_progress_bar=True)
    return ids, np.array(vectors), {pid: p for pid, p in zip(ids, products)}

def search_catalog(query, ids, vectors, product_map, embed_model, top_k=5):
    q_vec = np.array(embed_model.encode([query])[0])
    sims = np.dot(vectors, q_vec) / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(q_vec))
    best_idxs = np.argsort(-sims)[:top_k]
    return [product_map[ids[i]] for i in best_idxs]
