from dataclasses import dataclass
import re


@dataclass
class TranscriptChunk:
    content: str
    timestamp: str
    chunk_index: int


TIMESTAMP_PATTERN = re.compile(
    r"(?P<timestamp>"
    r"\[?\b(?:\d{1,2}:)?\d{1,2}:\d{2}\b\]?"
    r")"
)


def _normalize(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_transcript(
    text: str,
    max_chars: int = 2200,
    overlap_chars: int = 300,
) -> list[TranscriptChunk]:

    text = _normalize(text)

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks: list[TranscriptChunk] = []

    current_parts: list[str] = []
    current_length = 0
    current_timestamp = ""

    for paragraph in paragraphs:

        timestamp_match = TIMESTAMP_PATTERN.search(paragraph)

        if timestamp_match and not current_timestamp:
            current_timestamp = timestamp_match.group("timestamp")

        paragraph_length = len(paragraph)

        if (
            current_parts
            and current_length + paragraph_length + 2 > max_chars
        ):
            chunk_text = "\n\n".join(current_parts).strip()

            if chunk_text:
                chunks.append(
                    TranscriptChunk(
                        content=chunk_text,
                        timestamp=current_timestamp,
                        chunk_index=len(chunks),
                    )
                )

            # Preserve a small overlap.
            overlap = chunk_text[-overlap_chars:]

            current_parts = [overlap, paragraph]
            current_length = len(overlap) + paragraph_length + 2

            timestamp_match = TIMESTAMP_PATTERN.search(paragraph)

            if timestamp_match:
                current_timestamp = timestamp_match.group("timestamp")

        else:
            current_parts.append(paragraph)
            current_length += paragraph_length + 2

    if current_parts:
        chunk_text = "\n\n".join(current_parts).strip()

        if chunk_text:
            chunks.append(
                TranscriptChunk(
                    content=chunk_text,
                    timestamp=current_timestamp,
                    chunk_index=len(chunks),
                )
            )

    return chunks
