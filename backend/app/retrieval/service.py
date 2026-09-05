from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.transcript_chunk import TranscriptChunk


settings = get_settings()


@dataclass
class RetrievedChunk:
    id: str
    episode_title: str
    guest_name: str | None
    episode_url: str | None
    timestamp: str | None
    topic: str | None
    content: str
    similarity: float


async def retrieve_chunks(
    session: AsyncSession,
    query_embedding: list[float],
    top_k: int | None = None,
    threshold: float | None = None,
) -> list[RetrievedChunk]:
    """
    Retrieve the most relevant transcript chunks using
    pgvector cosine similarity.
    """

    top_k = top_k or settings.retrieval_top_k
    threshold = (
        settings.retrieval_threshold
        if threshold is None
        else threshold
    )

    distance = TranscriptChunk.embedding.cosine_distance(
        query_embedding
    )

    result = await session.execute(
        select(
            TranscriptChunk,
            distance.label("distance"),
        )
        .where(TranscriptChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )

    rows = result.all()

    retrieved: list[RetrievedChunk] = []

    for chunk, distance_value in rows:
        similarity = 1.0 - float(distance_value)

        if similarity < threshold:
            continue

        retrieved.append(
            RetrievedChunk(
                id=str(chunk.id),
                episode_title=chunk.episode_title,
                guest_name=chunk.guest_name,
                episode_url=chunk.episode_url,
                timestamp=chunk.timestamp,
                topic=chunk.topic,
                content=chunk.content,
                similarity=similarity,
            )
        )

    return retrieved
