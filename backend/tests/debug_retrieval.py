import asyncio

from sqlalchemy import select, func

from app.database import AsyncSessionLocal
from app.ingestion.embedder import embed_texts
from app.models.transcript_chunk import TranscriptChunk


async def main():
    question = "How should a founder know when it is time to leave their job?"

    query_embedding = embed_texts([question])[0]

    async with AsyncSessionLocal() as session:

        total_result = await session.execute(
            select(func.count()).select_from(TranscriptChunk)
        )

        total = total_result.scalar_one()

        print(f"TOTAL CHUNKS: {total}")

        distance = TranscriptChunk.embedding.cosine_distance(
            query_embedding
        )

        result = await session.execute(
            select(
                TranscriptChunk.episode_title,
                TranscriptChunk.guest_name,
                distance.label("distance"),
            )
            .where(TranscriptChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(5)
        )

        rows = result.all()

        print(f"RAW VECTOR RESULTS: {len(rows)}")

        for row in rows:
            print()
            print(f"Episode: {row.episode_title}")
            print(f"Guest: {row.guest_name}")
            print(f"Distance: {row.distance}")
            print(f"Similarity: {1.0 - float(row.distance):.4f}")


if __name__ == "__main__":
    asyncio.run(main())
