import re
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import faiss, pickle
from sentence_transformers import SentenceTransformer
import numpy as np

from backend.config import settings

EMBED_MODEL = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "./data/faiss_db/product_index.faiss"
METADATA_PATH = "./data/faiss_db/product_metadata.pkl"

model = SentenceTransformer(EMBED_MODEL)
index = faiss.read_index(FAISS_INDEX_PATH)
with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)

def initialize_llm(settings):
    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL,
        temperature=0.7,
        base_url=settings.OPENAI_API_BASE_URL,
    )

def format_response(text, max_lines=5, use_bullets=True):
    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if use_bullets and len(lines) > 1:
        formatted = "\n".join([f"• {line}" if not line.startswith("•") else line for line in lines])
    else:
        formatted = "\n".join(lines)
    return formatted if formatted else "• No results found."

import re
import requests
import numpy as np
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def semantic_search_catalog(query, k=10):
    """
    Search local FAISS index with keyword filtering.
    Only returns products that have at least one query keyword in Description.
    """
    query_keywords = set(re.findall(r'\w+', query.lower()))
    print(f"[DEBUG] Query: {query}")
    print(f"[DEBUG] Keywords extracted: {query_keywords}")
    
    query_embedding = model.encode([query], normalize_embeddings=True)
    D, I = index.search(np.array(query_embedding).astype('float32'), k)
    
    results = []
    for idx, i in enumerate(I[0]):
        desc = (metadata[i].get('Description') or '').lower()
        stock = (metadata[i].get('StockCode') or '').strip()
        source = (metadata[i].get('Source') or 'Unknown').strip()
        
        # Check if any keyword matches in description
        keyword_match = any(qk in desc for qk in query_keywords)
        print(f"[DEBUG] Product {idx}: {desc[:50]}... | Source: {source} | Match: {keyword_match}")
        
        if keyword_match and desc.strip():
            results.append(metadata[i])
    
    print(f"[DEBUG] Catalog matches found: {len(results)}")
    return results


def search_web_api_for_product(query):
    """
    Search external API (Fakestore) with keyword filtering.
    Only returns products where query keywords match title or category.
    """
    products = []
    query_keywords = set(re.findall(r'\w+', query.lower()))
    print(f"[DEBUG] Searching API for keywords: {query_keywords}")
    
    try:
        api_resp = requests.get("https://fakestoreapi.com/products").json()
        for item in api_resp:
            title = item.get("title", "").lower()
            category = item.get("category", "").lower()
            
            # Check if ANY keyword appears in title or category
            keyword_match = any(qk in title or qk in category for qk in query_keywords)
            
            if keyword_match:
                products.append({
                    "Description": item.get("title"),
                    "UnitPrice": item.get("price"),
                    "Source": "Fakestore API",
                    "Country": item.get("category"),
                    "ImageURL": item.get("image"),
                    "StockCode": item.get("id"),
                })
                print(f"[DEBUG] API Match: {item.get('title')[:50]}... | Category: {category}")
    except Exception as e:
        print(f"[ERROR] API error: {e}")
    
    print(f"[DEBUG] API matches found: {len(products)}")
    return products


def product_search_pipeline(query):
    """
    1. Search local catalog first (with keyword filtering).
    2. If nothing found, search API (with keyword filtering).
    Returns products with Source field populated.
    """
    print(f"\n=== SEARCH PIPELINE STARTED ===")
    
    # Step 1: Try local catalog
    catalog_products = semantic_search_catalog(query, k=10)
    
    if catalog_products:
        print(f"[RESULT] Found {len(catalog_products)} products in local catalog. NOT checking API.")
        return catalog_products
    
    print(f"[RESULT] No products in local catalog. Checking API...")
    
    # Step 2: Fallback to API
    api_products = search_web_api_for_product(query)
    print(f"[RESULT] Found {len(api_products)} products from API.")
    return api_products


def rag_qa_node(state, llm):
    """
    Recommends products using local catalog first, then web API fallback.
    Displays results with Source clearly marked.
    """
    last_message = state.get("messages", [])[-1].content if state.get("messages") else ""
    found_products = product_search_pipeline(last_message)
    
    if found_products:
        lines = ["Best matching products:"]
        for i, p in enumerate(found_products, 1):
            name = (p.get('Description') or p.get('title') or p.get('name', '')).strip()
            price = str(p.get('UnitPrice') or p.get('price', '')).strip()
            source = (p.get('Source') or "Unknown").strip()
            lines.append(f"{i}. {name} ({source}) – ₹{price}")
        response_text = "\n".join(lines)
    else:
        response_text = "Sorry, no matching products found in our catalog or web APIs."
    
    msgs = state.get("messages", [])
    msgs.append(AIMessage(content=response_text))
    return {
        "messages": msgs,
        "next_action": "end_conversation",
        "recommended_products": found_products
    }

def analyze_intent_node(state, llm):
    last_message = state.get("messages", [])[-1].content if state.get("messages") else ""
    catalog_keywords = [
        "suggest", "recommend", "find", "show", "have", "catalog", "product", "item", "price", "cost", 
        "available", "buy", "order", "pair", "sneaker", "shoes", "watch", "shirt", "jeans", "t-shirt", 
        "api", "under", "₹", "$", "tv", "laptop", "phone", "television", "smart", "display", "monitor"
    ]
    # Lowercased word check:
    message_words = set(last_message.lower().split())
    if any(kw in last_message.lower() or kw in message_words for kw in catalog_keywords):
        return {"next_action": "rag_qa", "messages": state.get("messages", [])}
    return {"next_action": "general_chat", "messages": state.get("messages", [])}

def general_chat_node(state, llm):
    last_message = state.get("messages", [])[-1].content if state.get("messages") else ""
    system_prompt = (
        "You are a helpful e-commerce AI assistant. "
        "Answer as a friendly shopping agent. Max 5 lines. No citations."
    )
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=last_message)])
    formatted_response = format_response(response.content)
    msgs = state.get("messages", [])
    msgs.append(AIMessage(content=formatted_response))
    return {
        "messages": msgs,
        "next_action": "end_conversation"
    }

def create_agent_graph(product_catalog, settings):
    llm = initialize_llm(settings)
    graph_builder = StateGraph(dict)
    graph_builder.add_node("analyze_intent", lambda s: analyze_intent_node(s, llm))
    graph_builder.add_node("general_chat", lambda s: general_chat_node(s, llm))
    graph_builder.add_node("rag_qa", lambda s: rag_qa_node(s, llm))
    graph_builder.set_entry_point("analyze_intent")
    graph_builder.add_conditional_edges(
        "analyze_intent",
        lambda state: state["next_action"],
        {
            "general_chat": "general_chat",
            "rag_qa": "rag_qa",
            END: END
        }
    )
    graph_builder.add_edge("general_chat", END)
    graph_builder.add_edge("rag_qa", END)
    agent_graph = graph_builder.compile()
    return agent_graph
