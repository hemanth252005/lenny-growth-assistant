import asyncio

from app.database import AsyncSessionLocal
from app.ingestion.embedder import embed_texts
from app.retrieval.context import build_grounded_context
from app.retrieval.service import retrieve_chunks


async def main():
    question = (
        "How should a founder know when it is time to "
        "leave their job?"
    )

    query_embedding = embed_texts([question])[0]

    async with AsyncSessionLocal() as session:
        results = await retrieve_chunks(
            session=session,
            query_embedding=query_embedding,
            top_k=5,
            threshold=0.45,
        )

    print()
    print("=" * 80)
    print("GROUNDED CONTEXT TEST")
    print("=" * 80)
    print(f"Question: {question}")
    print(f"Retrieved chunks: {len(results)}")
    print()

    context = build_grounded_context(results)

    print(context)


if __name__ == "__main__":
    asyncio.run(main())
