import re
from dataclasses import dataclass


@dataclass
class TranscriptChunk:
    content: str
    chunk_index: int
    timestamp: str | None = None
    topic: str | None = None


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_into_chunks(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[TranscriptChunk]:
    text = clean_text(text)

    if not text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks: list[TranscriptChunk] = []

    current = ""
    chunk_index = 0

    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = (
                f"{current}\n\n{paragraph}"
                if current
                else paragraph
            )
            continue

        if current:
            chunks.append(
                TranscriptChunk(
                    content=current.strip(),
                    chunk_index=chunk_index,
                )
            )

            chunk_index += 1

            overlap_text = current[-overlap:]

            current = (
                f"{overlap_text}\n\n{paragraph}"
            )
        else:
            chunks.append(
                TranscriptChunk(
                    content=paragraph[:chunk_size].strip(),
                    chunk_index=chunk_index,
                )
            )

            chunk_index += 1

            current = paragraph[chunk_size - overlap:]

    if current.strip():
        chunks.append(
            TranscriptChunk(
                content=current.strip(),
                chunk_index=chunk_index,
            )
        )

    return chunks
