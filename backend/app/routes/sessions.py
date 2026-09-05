import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.message import Message
from app.models.session import Session

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("")
async def create_session(
    session: AsyncSession = Depends(get_db),
):
    new_session = Session(
        id=uuid.uuid4(),
        title="New conversation",
        provider="ollama",
    )

    session.add(new_session)
    await session.commit()
    await session.refresh(new_session)

    return {
        "session_id": str(new_session.id),
        "title": new_session.title,
        "created_at": new_session.created_at,
    }


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    session: AsyncSession = Depends(get_db),
):
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

    messages_result = await session.execute(
        select(Message)
        .where(Message.session_id == session_uuid)
        .order_by(Message.created_at.asc())
    )

    messages = messages_result.scalars().all()

    return {
        "session_id": str(chat_session.id),
        "title": chat_session.title,
        "created_at": chat_session.created_at,
        "updated_at": chat_session.updated_at,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at,
            }
            for m in messages
        ],
    }
