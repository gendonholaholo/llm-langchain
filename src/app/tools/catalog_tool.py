"""Catalog search tool for the agent."""

from langchain_core.tools import tool

from app.rag.retriever import retrieve_documents


@tool
async def search_catalog(query: str) -> str:
    """Search the product/service catalog for specific items, pricing, or availability."""
    docs = await retrieve_documents(query)
    if not docs:
        return "No matching products or services found in the catalog."
    return "\n\n---\n\n".join(docs)
