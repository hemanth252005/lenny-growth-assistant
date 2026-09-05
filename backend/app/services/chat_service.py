import uuid
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.ingestion.embedder import embed_texts
from app.llm.factory import get_llm_provider
from app.llm.prompts import (
    FALLBACK_MESSAGE,
    GROUNDED_SYSTEM_PROMPT,
    build_user_prompt,
)
from app.models.message import Message
from app.models.session import Session
from app.retrieval.context import build_grounded_context
from app.retrieval.service import retrieve_chunks


async def save_message(
    session: AsyncSession,
    session_id: str,
    role: str,
    content: str,
) -> None:
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID",
        )

    result = await session.execute(
        select(Session).where(Session.id == session_uuid)
    )

    chat_session = result.scalar_one_or_none()

    if chat_session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    message = Message(
        id=uuid.uuid4(),
        session_id=session_uuid,
        role=role,
        content=content,
    )

    session.add(message)
    chat_session.updated_at = datetime.utcnow()

    await session.commit()


async def get_conversation_messages(
    session: AsyncSession,
    session_id: str,
    limit: int = 8,
) -> list[Message]:
    """
    Load the most recent messages from the current session.
    """

    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        return []

    result = await session.execute(
        select(Message)
        .where(Message.session_id == session_uuid)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    messages = list(result.scalars().all())

    # Newest -> oldest from DB.
    # Reverse so the model sees chronological order.
    messages.reverse()

    return messages


def format_conversation_history(
    messages: list[Message],
) -> str:
    """
    Format recent conversation for the LLM.
    """

    if not messages:
        return ""

    history_parts = []

    for message in messages:
        content = message.content.strip()

        # Protect the local model context window.
        if len(content) > 1200:
            content = (
                content[:1200].rsplit(" ", 1)[0]
                + "..."
            )

        role = message.role.capitalize()

        history_parts.append(
            f"{role}: {content}"
        )

    return "\n".join(history_parts)


def build_contextual_retrieval_query(
    question: str,
    messages: list[Message],
) -> str:
    """
    Resolve follow-up questions such as:

    Previous:
    "What did Varun Mohan say about Windsurf?"

    Current:
    "What did he say about it?"

    Retrieval should search using both pieces of context.
    """

    if not messages:
        return question

    # Only use previous USER questions for retrieval context.
    # This avoids letting an old model answer become the retrieval source.
    previous_user_questions = [
        message.content.strip()
        for message in messages
        if message.role == "user"
        and message.content.strip()
        and message.content.strip() != question.strip()
    ]

    # Keep retrieval query compact.
    previous_user_questions = previous_user_questions[-3:]

    if not previous_user_questions:
        return question

    previous_context = "\n".join(
        previous_user_questions
    )

    return f"""
Previous user questions:
{previous_context}

Current user question:
{question}

Resolve references such as:
- he
- she
- they
- it
- this
- that
- them

Use the previous user questions only to understand what
the current question refers to.
""".strip()


def build_question_with_history(
    question: str,
    conversation_history: str,
) -> str:
    """
    Build the LLM question containing recent conversation context.
    """

    if not conversation_history:
        return question

    return f"""
RECENT CONVERSATION
-------------------
{conversation_history}

CURRENT USER QUESTION
---------------------
{question}

Use the recent conversation only to understand references such as
"it", "they", "that", "this", "he", or "she".

Answer using ONLY the supplied Lenny's Podcast transcript evidence.
Do not use outside knowledge.
""".strip()


async def prepare_chat(
    session: AsyncSession,
    question: str,
    provider: str | None = None,
    session_id: str | None = None,
):
    settings = get_settings()

    # ---------------------------------------------------------
    # 1. Save current user message
    # ---------------------------------------------------------
    if session_id:
        await save_message(
            session,
            session_id,
            "user",
            question,
        )

    # ---------------------------------------------------------
    # 2. Load conversation history
    # ---------------------------------------------------------
    conversation_messages: list[Message] = []

    if session_id:
        conversation_messages = (
            await get_conversation_messages(
                session,
                session_id,
                limit=8,
            )
        )

    conversation_history = (
        format_conversation_history(
            conversation_messages
        )
    )

    # ---------------------------------------------------------
    # 3. Build contextual question for the LLM
    # ---------------------------------------------------------
    question_with_history = (
        build_question_with_history(
            question,
            conversation_history,
        )
    )

    # ---------------------------------------------------------
    # 4. IMPORTANT:
    # Build the retrieval query using conversation history.
    #
    # This fixes:
    #
    # "What did Varun say about Windsurf?"
    # ->
    # "What did he say about it?"
    #
    # The second question alone is too vague for vector search.
    # ---------------------------------------------------------
    retrieval_query = (
        build_contextual_retrieval_query(
            question,
            conversation_messages,
        )
    )

    # ---------------------------------------------------------
    # 5. Generate embedding from contextual retrieval query
    # ---------------------------------------------------------
    query_embedding = embed_texts(
        [retrieval_query]
    )[0]

    # ---------------------------------------------------------
    # 6. Retrieve transcript evidence
    # ---------------------------------------------------------
    chunks = await retrieve_chunks(
        session,
        query_embedding,
        top_k=settings.retrieval_top_k,
        threshold=settings.retrieval_threshold,
    )

    selected_provider = (
        provider
        or settings.default_llm_provider
    ).lower()

    # ---------------------------------------------------------
    # 7. No evidence -> exact grounded fallback
    # ---------------------------------------------------------
    if not chunks:
        answer = FALLBACK_MESSAGE

        if session_id:
            await save_message(
                session,
                session_id,
                "assistant",
                answer,
            )

        return (
            answer,
            [],
            selected_provider,
        )

    # ---------------------------------------------------------
    # 8. Build transcript context
    # ---------------------------------------------------------
    context = build_grounded_context(
        chunks
    )

    # ---------------------------------------------------------
    # 9. Claude Agent SDK
    # ---------------------------------------------------------
    if selected_provider == "claude":

        try:
            from app.services.agent_service import (
                run_claude_agent,
            )

            answer = await run_claude_agent(
                question=question_with_history,
                transcript_context=context,
            )

        except Exception:
            # Claude unavailable or API key missing.
            # Fall back to mandatory local Ollama.
            ollama_provider = get_llm_provider(
                "ollama"
            )

            user_prompt = build_user_prompt(
                question_with_history,
                context,
            )

            answer = await ollama_provider.generate(
                system_prompt=GROUNDED_SYSTEM_PROMPT,
                user_prompt=user_prompt,
            )

            selected_provider = "ollama"

    # ---------------------------------------------------------
    # 10. Ollama / configured provider
    # ---------------------------------------------------------
    else:

        user_prompt = build_user_prompt(
            question_with_history,
            context,
        )

        llm_provider = get_llm_provider(
            selected_provider
        )

        answer = await llm_provider.generate(
            system_prompt=GROUNDED_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    # ---------------------------------------------------------
    # 11. Save assistant response
    # ---------------------------------------------------------
    if session_id:
        await save_message(
            session,
            session_id,
            "assistant",
            answer,
        )

    return (
        answer,
        chunks,
        selected_provider,
    )
