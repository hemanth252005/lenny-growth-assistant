from app.llm.factory import get_llm_provider
from app.llm.ollama import OllamaProvider


def test_ollama_provider_factory():
    provider = get_llm_provider("ollama")

    assert isinstance(provider, OllamaProvider)


def test_ollama_provider_has_generate_method():
    provider = get_llm_provider("ollama")

    assert hasattr(provider, "generate")
    assert callable(provider.generate)
