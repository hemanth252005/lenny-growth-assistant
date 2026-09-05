import pytest

from app.database import AsyncSessionLocal
from app.services import chat_service


class FakeProvider:
    async def generate(self, system_prompt, user_prompt):
        return "Mocked grounded answer."


@pytest.mark.asyncio
async def test_prepare_chat_returns_grounded_response(monkeypatch):
    monkeypatch.setattr(
        chat_service,
        "get_llm_provider",
        lambda provider=None: FakeProvider(),
    )

    async with AsyncSessionLocal() as session:
        answer, chunks, provider = await chat_service.prepare_chat(
            session=session,
            question="What did Lenny's guests say about building products?",
            provider="ollama",
        )

    assert answer
    assert answer == "Mocked grounded answer."
    assert provider == "ollama"
    assert isinstance(chunks, list)
