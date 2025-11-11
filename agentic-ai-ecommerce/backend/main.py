from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessage
from backend.config import settings
from backend.agents.agent_graph import create_agent_graph, format_response, initialize_llm

import uuid

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dummy product catalog just for graph creation
product_catalog = []
agent_graph = create_agent_graph(product_catalog, settings)
conversation_states = {}

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    query = data.get("text", "")
    user_id = data.get("user_id", str(uuid.uuid4()))

    if user_id not in conversation_states:
        conversation_states[user_id] = {"messages": [], "user_preferences": {}, "recommended_products": [], "cart": []}
    conversation_state = conversation_states[user_id]
    conversation_state["messages"].append(HumanMessage(content=query))
    state = {
        "messages": conversation_state["messages"].copy(),
        "user_preferences": conversation_state["user_preferences"].copy(),
        "next_action": None,
        "recommended_products": conversation_state["recommended_products"].copy(),
    }
    config = {"recursion_limit": 10}
    output = agent_graph.invoke(state, config)
    conversation_state["messages"] = output.get("messages", [])
    conversation_state["user_preferences"] = output.get("user_preferences", {})
    conversation_state["recommended_products"] = output.get("recommended_products", [])
    msgs = output.get("messages", [])
    response_text = ""
    if msgs:
        last_msg = msgs[-1]
        if isinstance(last_msg, AIMessage):
            response_text = last_msg.content
        elif len(msgs) > 1 and isinstance(msgs[-2], AIMessage):
            response_text = msgs[-2].content
    response_text = format_response(
        response_text,
        max_lines=settings.MAX_RESPONSE_LINES,
        use_bullets=settings.USE_BULLET_POINTS
    )
    products = output.get("recommended_products", [])
    # --- HERE IS THE IMPORTANT CODE ---
    formatted_products = [
        {
            "id": p.get("StockCode") or p.get("id", ""),
            "name": p.get("Description") or p.get("title") or p.get("name", ""),
            "price": p.get("UnitPrice") or p.get("price", 0),
            "description": p.get("Description") or p.get("description") or p.get("title", ""),
            "source": p.get("Source", "Internal"),
            "image_url": p.get("ImageURL", "https://via.placeholder.com/200"),
            "country": p.get("Country", ""),
            "category": p.get("Category", "")
        }
        for p in products
        if (p.get("Description") or p.get("title") or p.get("name", "")).strip()
    ]
    return {
        "response": response_text,
        "products": formatted_products,
        "next_action": output.get("next_action", "end_conversation"),
        "cart_items": conversation_state.get("cart", []),
        "order_id": None,
        "loading": False,
    }
