# 🛒 Agentic AI E-commerce — End-to-End GenAI Product Search & Chat

## Project Overview
This project is a fully local, agentic e-commerce AI assistant built with FastAPI, RAG (Retrieval Augmented Generation), and semantic search powered by FAISS and Sentence Transformers. Users can chat about products, receive recommendations, and trigger agentic workflows. Designed for extensibility and rapid Azure/Databricks/LLM integration.

---

## Folder Structure
agentic-ai-ecommerce/
├── backend/
│ ├── main.py
│ ├── rag/
│ │ ├── csv2txt.py
│ │ ├── ingest.py
│ │ ├── embedder.py
│ ├── routes/
│ │ ├── admin.py
│ ├── utils/
│ │ ├── recommendations.py
│ │ ├── vector_search.py
├── frontend/
│ ├── index.html
│ ├── admin.html
├── data/
│ ├── kaggle_ecom.csv
│ ├── rag_docs/
│ │ └── products.txt
│ ├── faiss_db/
│ │ ├── index.faiss
│ │ └── metadata.pkl
├── .env
├── requirements.txt
├── README.md
└── bash_guide.txt


---

## Key Features
- Product search via semantic embeddings (Sentence Transformers + FAISS)
- RAG product QA (LLMs can answer domain/product questions using indexed docs)
- FastAPI backend for chat, admin, recommendations
- Frontend for chat and admin (static HTML, ready to extend)
- Configurable via `.env` file

---

## Configuration
Edit your `.env` for settings and API keys:

SERVER_HOST=0.0.0.0
SERVER_PORT=8000
PRODUCT_CATALOG_PATH=./data/kaggle_ecom.csv
OPENAI_API_KEY=your_api_key_here
RAG_FAISS_DB_DIR=./data/faiss_db
RAG_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2



---

## Prerequisites
- Windows (tested) or Linux
- Python 3.12.x
- All dependencies in `requirements.txt` (use pip)

---

## Running The Project

See the `bash_guide.txt` file for step-by-step commands!

---

## Troubleshooting

- **DLL/module errors:** Uninstall/reinstall the affected package(s) with `--no-cache-dir`.
- **Build errors:** Always use Python ≤3.12.
- **Missing wheels:** Install scientific packages (numpy, pandas, scikit-learn) first.
- **Long thread warning:** Start a new chat and paste this README as context!

---

## Credits & Support

Built for agentic RAG/AI engineering learning and interview prep.
Quickly extend with custom agents, product APIs, or Azure endpoints.
Contact/support: continue in your workspace or open a new thread with this README for context.

