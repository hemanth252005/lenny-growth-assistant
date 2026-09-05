import asyncio

from sqlalchemy import text

from app.database import engine
from app.models import Base

# Import every model so SQLAlchemy registers every table.
from app.models import (
    Artifact,
    Message,
    Session,
    TranscriptChunk,
)


async def init_db() -> None:
    async with engine.begin() as connection:

        # Enable pgvector.
        await connection.execute(
            text("CREATE EXTENSION IF NOT EXISTS vector")
        )

        # Create all registered tables.
        await connection.run_sync(
            Base.metadata.create_all
        )


async def main() -> None:
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully.")


if __name__ == "__main__":
    asyncio.run(main())
