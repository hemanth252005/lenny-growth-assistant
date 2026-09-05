from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User question about Lenny's Podcast",
    )

    provider: str | None = Field(
        default=None,
        description="LLM provider, e.g. ollama",
    )

    session_id: str | None = Field(
        default=None,
        description="Optional chat session identifier",
    )


class SourceCitation(BaseModel):
    episode_title: str
    guest_name: str | None = None
    timestamp: str | None = None
    topic: str | None = None
    episode_url: str | None = None
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceCitation] = Field(default_factory=list)
    provider: str
    grounded: bool
