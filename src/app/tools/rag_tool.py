"""RAG search tool for the agent."""

from langchain_core.tools import tool

from app.rag.retriever import retrieve_documents


@tool
async def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for relevant information about products and services."""
    docs = await retrieve_documents(query)
    if not docs:
        return "No relevant information found in the knowledge base."
    return "\n\n---\n\n".join(docs)
