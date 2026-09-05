from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class TranscriptChunkData:
    episode_title: str
    guest_name: str | None
    episode_url: str | None
    timestamp: str | None
    topic: str | None
    content: str
    chunk_index: int


FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL,
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_PATTERN.match(text)

    if not match:
        return {}, text

    raw_frontmatter = match.group(1)
    body = text[match.end():]

    metadata: dict[str, str] = {}

    for line in raw_frontmatter.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip().strip('"').strip("'")

        metadata[key] = value

    return metadata, body


def clean_transcript(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)

    text = re.sub(
        r"^\s*##?\s*Transcript\s*$",
        "",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_guest(metadata: dict[str, str]) -> str | None:
    guest = metadata.get("guest")

    if guest:
        return guest

    title = metadata.get("title", "")

    if "|" in title:
        possible_guest = title.rsplit("|", 1)[-1].strip()

        if possible_guest:
            return possible_guest

    return None


def split_into_chunks(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:

        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = (
                f"{current}\n\n{paragraph}"
                if current
                else paragraph
            )
            continue

        if current:
            chunks.append(current.strip())

        overlap_text = current[-overlap:] if current else ""

        current = (
            f"{overlap_text}\n\n{paragraph}"
            if overlap_text
            else paragraph
        )

    if current:
        chunks.append(current.strip())

    return chunks


def parse_transcript_file(
    path: Path,
) -> list[TranscriptChunkData]:

    raw_text = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    metadata, body = parse_frontmatter(raw_text)

    body = clean_transcript(body)

    if not body:
        return []

    episode_title = metadata.get(
        "title",
        path.parent.name,
    )

    guest_name = extract_guest(metadata)

    episode_url = (
        metadata.get("youtube_url")
        or metadata.get("url")
    )

    chunks = split_into_chunks(body)

    result: list[TranscriptChunkData] = []

    for index, chunk in enumerate(chunks):

        timestamp_match = re.search(
            r"\((\d{1,2}:\d{2}(?::\d{2})?)\)",
            chunk,
        )

        timestamp = (
            timestamp_match.group(1)
            if timestamp_match
            else None
        )

        result.append(
            TranscriptChunkData(
                episode_title=episode_title,
                guest_name=guest_name,
                episode_url=episode_url,
                timestamp=timestamp,
                topic=None,
                content=chunk,
                chunk_index=index,
            )
        )

    return result


def find_transcript_files(
    transcripts_root: Path,
) -> list[Path]:

    return sorted(
        transcripts_root.glob(
            "episodes/**/transcript.md"
        )
    )
