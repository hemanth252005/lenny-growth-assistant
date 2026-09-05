from app.config import get_settings
from app.llm.base import LLMProvider
from app.llm.ollama import OllamaProvider


def get_llm_provider(
    provider: str | None = None,
) -> LLMProvider:

    settings = get_settings()

    selected_provider = (
        provider or settings.default_llm_provider
    ).lower()

    if selected_provider == "ollama":
        return OllamaProvider()

    raise ValueError(
        f"Unsupported LLM provider: {selected_provider}"
    )
