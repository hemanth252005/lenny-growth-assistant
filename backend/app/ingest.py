import asyncio
import logging
from pathlib import Path

from app.database import AsyncSessionLocal
from app.ingestion.pipeline import ingest_all


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("lenny.ingest")


async def main() -> None:
    transcript_root = Path("/app/data/lenny_transcripts/episodes")

    if not transcript_root.exists():
        raise FileNotFoundError(
            f"Transcript directory does not exist: {transcript_root}"
        )

    async with AsyncSessionLocal() as session:
        episodes, chunks = await ingest_all(
            session=session,
            root=transcript_root,
        )

    logger.info(
        "INGESTION COMPLETE | episodes=%d | chunks=%d",
        episodes,
        chunks,
    )


if __name__ == "__main__":
    asyncio.run(main())
