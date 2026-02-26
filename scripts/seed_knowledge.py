"""Seed knowledge base with documents from data/knowledge/."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from app.rag.ingest import ingest_documents  # noqa: E402


async def main() -> None:
    print("Seeding knowledge base...")
    count = await ingest_documents()
    print(f"Ingested {count} chunks into vector store.")


if __name__ == "__main__":
    asyncio.run(main())
