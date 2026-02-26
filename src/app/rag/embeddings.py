"""OpenAI embeddings and PGVector store setup."""

from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

from app.constants import ModelName
from app.core.config import settings

embeddings = OpenAIEmbeddings(model=ModelName.EMBEDDING, openai_api_key=settings.openai_api_key)


def get_vector_store() -> PGVector:
    """Get PGVector store instance."""
    return PGVector(
        embeddings=embeddings,
        collection_name="documents",
        connection=settings.database_url,
        use_jsonb=True,
    )
