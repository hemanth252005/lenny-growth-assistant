from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.ingestion.embedder import embed_texts
from app.retrieval.context import build_grounded_context
from app.retrieval.service import retrieve_chunks
from app.services.ship30_service import generate_ship30_essay
from app.llm.prompts import FALLBACK_MESSAGE


router = APIRouter(
    prefix="/api/ship30",
    tags=["Ship30"],
)


class Ship30Request(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
    )
    provider: str = Field(
        default="ollama",
    )


class Ship30Response(BaseModel):
    essay: str
    sources: list[dict]
    provider: str
    grounded: bool


@router.post("", response_model=Ship30Response)
async def create_ship30_essay(
    request: Ship30Request,
    session: AsyncSession = Depends(get_db),
):
    query_embedding = embed_texts([request.question])[0]

    chunks = await retrieve_chunks(
        session,
        query_embedding,
    )

    if not chunks:
        return Ship30Response(
            essay=FALLBACK_MESSAGE,
            sources=[],
            provider=request.provider,
            grounded=False,
        )

    context = build_grounded_context(chunks)

    # First establish the grounded research answer.
    from app.llm.factory import get_llm_provider
    from app.llm.prompts import (
        GROUNDED_SYSTEM_PROMPT,
        build_user_prompt,
    )

    provider = request.provider.lower()

    try:
        llm_provider = get_llm_provider(provider)

        grounded_answer = await llm_provider.generate(
            system_prompt=GROUNDED_SYSTEM_PROMPT,
            user_prompt=build_user_prompt(
                request.question,
                context,
            ),
        )

        essay = await generate_ship30_essay(
            question=request.question,
            grounded_answer=grounded_answer,
            transcript_context=context,
            provider=provider,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ship30 generation failed: {str(exc)}",
        )

    sources = [
        {
            "episode_title": chunk.episode_title,
            "guest_name": chunk.guest_name,
            "timestamp": chunk.timestamp,
            "topic": chunk.topic,
            "episode_url": chunk.episode_url,
            "similarity": chunk.similarity,
        }
        for chunk in chunks
    ]

    return Ship30Response(
        essay=essay,
        sources=sources,
        provider=provider,
        grounded=True,
    )
