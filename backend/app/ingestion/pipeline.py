import logging
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.ingestion.chunker import chunk_transcript
from app.ingestion.embedder import embed_texts
from app.ingestion.parser import parse_transcript
from app.models.transcript_chunk import TranscriptChunk


logger = logging.getLogger("lenny.ingestion")


async def ingest_episode(
    session: AsyncSession,
    transcript_path: Path,
) -> int:
    episode = parse_transcript(transcript_path)

    chunks = chunk_transcript(episode.content)

    if not chunks:
        logger.warning(
            "No chunks generated | file=%s",
            transcript_path,
        )
        return 0

    # Idempotency:
    # Prefer the episode URL as the stable identifier.
    # Fall back to title when the URL is unavailable.
    if episode.episode_url:
        await session.execute(
            delete(TranscriptChunk).where(
                TranscriptChunk.episode_url == episode.episode_url
            )
        )
    else:
        await session.execute(
            delete(TranscriptChunk).where(
                TranscriptChunk.episode_title == episode.episode_title
            )
        )

    texts = [chunk.content for chunk in chunks]

    embeddings = embed_texts(texts)

    rows = []

    for chunk_index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        rows.append(
            TranscriptChunk(
                id=uuid4(),
                episode_title=episode.episode_title,
                guest_name=episode.guest_name,
                episode_url=episode.episode_url,
                timestamp=chunk.timestamp,
                topic=episode.topic,
                content=chunk.content,
                chunk_index=chunk_index,
                embedding=embedding,
            )
        )

    session.add_all(rows)

    await session.commit()

    logger.info(
        "Ingested episode | guest=%s | title=%s | chunks=%d",
        episode.guest_name,
        episode.episode_title,
        len(rows),
    )

    return len(rows)


async def ingest_all(
    session: AsyncSession,
    root: Path,
) -> tuple[int, int]:

    transcript_files = sorted(
        root.glob("*/transcript.md")
    )

    logger.info(
        "Discovered %d transcript files | root=%s",
        len(transcript_files),
        root,
    )

    episode_count = 0
    chunk_count = 0

    for index, transcript_path in enumerate(
        transcript_files,
        start=1,
    ):
        try:
            logger.info(
                "Processing %d/%d | %s",
                index,
                len(transcript_files),
                transcript_path.parent.name,
            )

            count = await ingest_episode(
                session,
                transcript_path,
            )

            episode_count += 1
            chunk_count += count

        except Exception:
            logger.exception(
                "Failed to ingest | file=%s",
                transcript_path,
            )

    return episode_count, chunk_count
