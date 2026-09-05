from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re

import yaml


@dataclass
class TranscriptEpisode:
    guest_name: str
    episode_title: str
    episode_url: str
    content: str
    topic: str = ""
    keywords: list[str] = field(default_factory=list)


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def parse_transcript(path: Path) -> TranscriptEpisode:
    raw = path.read_text(encoding="utf-8")

    metadata: dict[str, Any] = {}
    content = raw

    # Parse YAML frontmatter.
    if raw.startswith("---"):
        parts = raw.split("---", 2)

        if len(parts) == 3:
            frontmatter = parts[1]
            content = parts[2]

            loaded = yaml.safe_load(frontmatter)
            if isinstance(loaded, dict):
                metadata = loaded

    guest_name = str(
        metadata.get("guest")
        or path.parent.name.replace("-", " ").title()
    ).strip()

    episode_title = str(
        metadata.get("title")
        or path.stem
    ).strip()

    episode_url = str(
        metadata.get("youtube_url")
        or ""
    ).strip()

    keywords = metadata.get("keywords") or []

    if not isinstance(keywords, list):
        keywords = [str(keywords)]

    keywords = [str(keyword).strip() for keyword in keywords]

    cleaned_content = _clean_text(content)

    if not cleaned_content:
        raise ValueError(f"Transcript is empty: {path}")

    topic = ", ".join(keywords[:8])

    return TranscriptEpisode(
        guest_name=guest_name,
        episode_title=episode_title,
        episode_url=episode_url,
        content=cleaned_content,
        topic=topic,
        keywords=keywords,
    )
