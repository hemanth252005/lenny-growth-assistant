from __future__ import annotations

from pathlib import Path

from sqlalchemy import delete, select

from app.database import AsyncSessionLocal
from app.ingestion.embedding_service import generate_embeddings
from app.ingestion.transcript_parser import (
    TranscriptChunkData,
    find_transcript_files,
    parse_transcript_file,
)
from app.models import TranscriptChunk


def load_all_chunks(
    transcripts_root: Path,
) -> list[TranscriptChunkData]:

    files = find_transcript_files(
        transcripts_root
    )

    print(
        f"Found {len(files)} transcript files."
    )

    all_chunks: list[TranscriptChunkData] = []

    for index, path in enumerate(files, start=1):

        try:
            chunks = parse_transcript_file(path)

            all_chunks.extend(chunks)

        except Exception as exc:
            print(
                f"Failed to parse {path}: {exc}"
            )

        if index % 25 == 0:
            print(
                f"Processed {index}/{len(files)} files..."
            )

    print(
        f"Created {len(all_chunks)} transcript chunks."
    )

    return all_chunks


async def ingest_transcripts(
    transcripts_root: Path,
) -> None:

    chunks = load_all_chunks(
        transcripts_root
    )

    if not chunks:
        print("No transcript chunks found.")
        return

    print("Generating embeddings...")

    texts = [
        chunk.content
        for chunk in chunks
    ]

    embeddings = generate_embeddings(texts)

    print(
        f"Generated {len(embeddings)} embeddings."
    )

    async with AsyncSessionLocal() as session:

        print(
            "Clearing existing transcript chunks..."
        )

        await session.execute(
            delete(TranscriptChunk)
        )

        records = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):
            records.append(
                TranscriptChunk(
                    episode_title=chunk.episode_title,
                    guest_name=chunk.guest_name,
                    episode_url=chunk.episode_url,
                    timestamp=chunk.timestamp,
                    topic=chunk.topic,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    embedding=embedding,
                )
            )

        session.add_all(records)

        await session.commit()

    print(
        f"Successfully inserted {len(records)} transcript chunks."
    )
