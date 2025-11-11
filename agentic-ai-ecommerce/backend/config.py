import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    # Product catalog
    PRODUCT_CATALOG_PATH: str = os.getenv("PRODUCT_CATALOG_PATH", "./data/products_catalog.json")
    # RAG
    RAG_DOCS_DIR: str = os.getenv("RAG_DOCS_DIR", "./data/rag_docs")
    RAG_FAISS_DB_DIR: str = os.getenv("RAG_FAISS_DB_DIR", "./data/faiss_db")
    RAG_EMBED_MODEL: str = os.getenv("RAG_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    # LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "sonar-pro")
    OPENAI_API_BASE_URL: str = os.getenv("OPENAI_API_BASE_URL", "https://api.perplexity.ai")
    # Output
    MAX_RESPONSE_LINES: int = 5
    USE_BULLET_POINTS: bool = True
    # Misc
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
