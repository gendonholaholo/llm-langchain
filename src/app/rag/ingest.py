"""Document loading, splitting, and upserting into pgvector."""

import os

import structlog
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.embeddings import get_vector_store

logger = structlog.get_logger(__name__)


async def ingest_documents(knowledge_dir: str = "data/knowledge") -> int:
    """Load documents from directory, split, and upsert into vector store."""
    if not os.path.exists(knowledge_dir):  # noqa: ASYNC240
        logger.warning("ingest.dir_not_found", path=knowledge_dir)
        return 0

    # Load PDFs
    pdf_loader = DirectoryLoader(
        knowledge_dir, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True
    )

    # Load text files
    txt_loader = DirectoryLoader(
        knowledge_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        show_progress=True,
        loader_kwargs={"encoding": "utf-8"},
    )

    docs = pdf_loader.load() + txt_loader.load()

    if not docs:
        logger.info("ingest.no_documents")
        return 0

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # Upsert into vector store
    store = get_vector_store()
    await store.aadd_documents(chunks)

    logger.info("ingest.completed", num_docs=len(docs), num_chunks=len(chunks))
    return len(chunks)
