import asyncio

from app.database import AsyncSessionLocal
from app.ingestion.embedder import embed_texts
from app.retrieval.context import build_grounded_context
from app.retrieval.service import retrieve_chunks


async def main():
    question = "How should a founder know when it is time to leave their job?"

    async with AsyncSessionLocal() as session:
        embedding = embed_texts([question])[0]

        chunks = await retrieve_chunks(
            session=session,
            query_embedding=embedding,
        )

    context = build_grounded_context(chunks)

    print("=" * 80)
    print(f"CHUNKS: {len(chunks)}")
    print(f"CONTEXT CHARACTERS: {len(context)}")
    print("=" * 80)
    print(context)


if __name__ == "__main__":
    asyncio.run(main())
