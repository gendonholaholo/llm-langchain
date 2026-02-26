"""Async retriever factory for RAG."""

import structlog

from app.constants import MAX_RAG_RESULTS
from app.rag.embeddings import get_vector_store

logger = structlog.get_logger(__name__)


async def retrieve_documents(query: str) -> list[str]:
    """Retrieve relevant document chunks from pgvector."""
    try:
        store = get_vector_store()
        results = await store.asimilarity_search(query, k=MAX_RAG_RESULTS)
        docs = [doc.page_content for doc in results]
        logger.info("rag.retrieved", query_length=len(query), num_docs=len(docs))
        return docs
    except Exception:
        logger.exception("rag.retrieval_failed")
        return []
