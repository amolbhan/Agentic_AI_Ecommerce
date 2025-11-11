import os

DOCS_DIR = os.getenv("RAG_DOCS_DIR", "./data/rag_docs")
FAISS_DB_DIR = os.getenv("RAG_FAISS_DB_DIR", "./data/faiss_db")
EMBEDDING_MODEL_NAME = os.getenv("RAG_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBED_DIM = 384
