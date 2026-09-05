import asyncio

from app.database import AsyncSessionLocal
from app.ingestion.embedder import embed_texts
from app.retrieval.service import retrieve_chunks


async def main():
    question = "What is the best way to treat a broken leg?"
    
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
    print("RAG RETRIEVAL TEST")
    print("=" * 80)
    print(f"Question: {question}")
    print(f"Results: {len(results)}")
    print()

    for index, result in enumerate(results, start=1):
        print(f"[{index}] Similarity: {result.similarity:.4f}")
        print(f"Guest: {result.guest_name}")
        print(f"Episode: {result.episode_title}")
        print(f"Timestamp: {result.timestamp}")
        print(f"Topic: {result.topic}")
        print(f"Content: {result.content[:300]}")
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())
