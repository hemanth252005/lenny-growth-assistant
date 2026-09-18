from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "The Lenny Growth Assistant"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/lenny_assistant"
    )

    default_llm_provider: str = "ollama"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    openai_api_key: str = ""
    openai_model: str = ""

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"

    agent_max_turns: int = 6

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    retrieval_top_k: int = 3
    retrieval_threshold: float = 0.45

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    # Render/PostgreSQL commonly provides a URL beginning with
    # postgres:// or postgresql://. Our application uses asyncpg.
    if settings.database_url.startswith("postgres://"):
        settings.database_url = settings.database_url.replace(
            "postgres://",
            "postgresql+asyncpg://",
            1,
        )
    elif settings.database_url.startswith("postgresql://"):
        settings.database_url = settings.database_url.replace(
            "postgresql://",
            "postgresql+asyncpg://",
            1,
        )

    return settings