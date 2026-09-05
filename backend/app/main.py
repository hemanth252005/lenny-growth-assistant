import logging

import httpx
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.routes.chat import router as chat_router
from app.routes.sessions import router as sessions_router
from app.routes.ship30 import router as ship30_router


settings = get_settings()


logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("lenny-growth-assistant")


app = FastAPI(
    title="The Lenny Growth Assistant",
    description=(
        "Evidence-grounded product and growth intelligence "
        "powered by Lenny's Podcast transcripts."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(chat_router)
app.include_router(sessions_router)
app.include_router(ship30_router)


@app.get("/api/health")
async def health_check(session: AsyncSession = Depends(get_db)):
    database_status = "healthy"
    ollama_status = "healthy"

    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        database_status = "unavailable"

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                f"{settings.ollama_base_url}/api/tags"
            )

            if response.status_code != 200:
                ollama_status = "unavailable"

    except Exception:
        ollama_status = "unavailable"

    overall_status = (
        "healthy"
        if database_status == "healthy"
        and ollama_status == "healthy"
        else "degraded"
    )

    return {
        "status": overall_status,
        "service": "lenny-growth-assistant",
        "database": database_status,
        "vector_index": database_status,
        "ollama": ollama_status,
        "provider": settings.default_llm_provider,
        "model": settings.ollama_model,
    }


@app.get("/")
async def root():
    return {
        "name": "The Lenny Growth Assistant",
        "status": "running",
    }
