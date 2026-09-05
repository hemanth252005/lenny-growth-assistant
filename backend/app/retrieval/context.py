from app.retrieval.service import RetrievedChunk


MAX_CHUNK_CHARS = 450


def format_source(chunk: RetrievedChunk) -> str:
    guest = chunk.guest_name or "Unknown Guest"
    timestamp = chunk.timestamp or "Unknown timestamp"
    topic = chunk.topic or "Transcript"

    return f"[Episode: {guest}, {timestamp}/{topic}]"


def build_grounded_context(
    chunks: list[RetrievedChunk],
) -> str:
    if not chunks:
        return ""

    sections = []

    for chunk in chunks[:3]:
        content = chunk.content.strip()

        if len(content) > MAX_CHUNK_CHARS:
            content = content[:MAX_CHUNK_CHARS].rsplit(" ", 1)[0] + "..."

        source = format_source(chunk)

        sections.append(
            f"{source}\n"
            f"{content}"
        )

    return "\n\n---\n\n".join(sections)
