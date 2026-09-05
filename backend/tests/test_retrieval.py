import pytest

from app.database import AsyncSessionLocal
from app.ingestion.embedder import embed_texts
from app.retrieval.service import retrieve_chunks


@pytest.mark.asyncio
async def test_retrieval_returns_valid_transcript_chunks():
    question = "What is the best way to treat a broken leg?"
    query_embedding = embed_texts([question])[0]

    async with AsyncSessionLocal() as session:
        results = await retrieve_chunks(
            session=session,
            query_embedding=query_embedding,
            top_k=5,
            threshold=0.45,
        )

    assert isinstance(results, list)
    assert len(results) <= 5

    for result in results:
        assert result.id
        assert result.episode_title
        assert result.content
        assert 0.0 <= result.similarity <= 1.0
