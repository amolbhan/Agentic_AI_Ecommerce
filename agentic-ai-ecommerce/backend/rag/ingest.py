import csv
import os
import numpy as np
import faiss
import pickle
import requests
from sentence_transformers import SentenceTransformer

CATALOG_PATH = "./data/kaggle_ecom.csv"
FAISS_INDEX_PATH = "./data/faiss_db/product_index.faiss"
METADATA_PATH = "./data/faiss_db/product_metadata.pkl"
EMBED_MODEL = "all-MiniLM-L6-v2"

# 1. Load your CSV products (add Source field)
products = []
with open(CATALOG_PATH, "r", encoding="latin1") as f:
    reader = csv.DictReader(f)
    for row in reader:
        row["Source"] = "Internal Catalog"
        products.append(row)

# 2. Get products from fakestoreapi.com
api_response = requests.get("https://fakestoreapi.com/products").json()
for api_product in api_response:
    products.append({
        "Description": api_product.get("title", ""),
        "UnitPrice": api_product.get("price", ""),
        "StockCode": api_product.get("id", ""),
        "Country": api_product.get("category", ""),
        "Source": "Fakestore API",
        "ImageURL": api_product.get("image", "")
    })

# 3. Embed each item as a document
docs = [
    f"{p.get('Description','')} {p.get('Country','')} {p.get('Source','')}"
    for p in products
]
metadata = products

model = SentenceTransformer(EMBED_MODEL)
embeddings = model.encode(docs, show_progress_bar=True, normalize_embeddings=True)
d = embeddings.shape[1]
index = faiss.IndexFlatIP(d)
index.add(np.array(embeddings).astype('float32'))

os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
faiss.write_index(index, FAISS_INDEX_PATH)
with open(METADATA_PATH, "wb") as f:
    pickle.dump(metadata, f)

print("✅ FAISS semantic index built and saved (catalog + fakestoreapi).")
