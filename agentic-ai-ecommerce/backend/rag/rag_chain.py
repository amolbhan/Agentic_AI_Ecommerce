from backend.rag.retriever import retrieve_relevant_chunks
from langchain_core.messages import HumanMessage, SystemMessage

def rag_prompt(query, retrieved_chunks):
    context = "\n\n".join([c["chunk"] for c in retrieved_chunks])
    return (
        "You are an AI assistant answering user questions using the following context retrieved from documents:\n"
        "---CONTEXT---\n"
        f"{context}\n"
        "---\n"
        "Answer very specifically using only the above information unless absolutely necessary to guess.\n"
        f"User question:\n{query}\n"
    )

def run_rag_chain(query, llm, top_k=4):
    chunks = retrieve_relevant_chunks(query, top_k=top_k)
    if not chunks:
        return {
            "response": "No relevant documents found to answer your question.",
            "sources": [],
            "chunks": []
        }
    prompt = rag_prompt(query, chunks)
    response = llm.invoke([SystemMessage(content=prompt), HumanMessage(content=query)])
    return {
        "response": response.content,
        "sources": [c["source"] for c in chunks if c.get("source")],
        "chunks": [c["chunk"] for c in chunks]
    }
