import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.ingestion.embedder import embed_texts
from app.llm.factory import get_llm_provider
from app.llm.prompts import (
    FALLBACK_MESSAGE,
    GROUNDED_SYSTEM_PROMPT,
    build_user_prompt,
)
from app.retrieval.context import build_grounded_context
from app.retrieval.service import retrieve_chunks
from app.schemas.chat import ChatRequest, ChatResponse, SourceCitation
from app.services.chat_service import prepare_chat


router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_db),
):
    answer, chunks, provider = await prepare_chat(
        session=session,
        question=request.question,
        provider=request.provider,
        session_id=request.session_id,
    )

    sources = [
        SourceCitation(
            episode_title=chunk.episode_title,
            guest_name=chunk.guest_name,
            timestamp=chunk.timestamp,
            topic=chunk.topic,
            episode_url=chunk.episode_url,
            similarity=chunk.similarity,
        )
        for chunk in chunks
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
        provider=provider,
        grounded=bool(chunks),
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    session: AsyncSession = Depends(get_db),
):
    async def generate():
        try:
            query_embedding = embed_texts([request.question])[0]

            chunks = await retrieve_chunks(
                session=session,
                query_embedding=query_embedding,
            )

            if not chunks:
                yield json.dumps({
                    "type": "done",
                    "answer": FALLBACK_MESSAGE,
                    "sources": [],
                    "provider": request.provider or "ollama",
                    "grounded": False,
                }) + "\n"
                return

            context = build_grounded_context(chunks)

            user_prompt = build_user_prompt(
                question=request.question,
                context=context,
            )

            provider_name = request.provider or "ollama"
            llm_provider = get_llm_provider(provider_name)

            full_answer = ""

            async for raw_chunk in llm_provider.stream(
                system_prompt=GROUNDED_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            ):
                try:
                    data = json.loads(raw_chunk)

                    if data.get("done"):
                        break

                    token = data.get("message", {}).get("content", "")

                    if token:
                        full_answer += token

                        yield json.dumps({
                            "type": "token",
                            "content": token,
                        }) + "\n"

                except json.JSONDecodeError:
                    continue

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

            yield json.dumps({
                "type": "done",
                "answer": full_answer,
                "sources": sources,
                "provider": provider_name,
                "grounded": True,
            }) + "\n"

        except Exception as exc:
            yield json.dumps({
                "type": "error",
                "message": str(exc),
            }) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
