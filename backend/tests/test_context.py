import pytest

from app.ingestion.embedder import embed_texts
from app.retrieval.context import build_grounded_context
from app.retrieval.service import retrieve_chunks


@pytest.mark.asyncio
async def test_grounded_context_contains_retrieved_transcript_data():
    question = "How should a founder know when it is time to leave their job?"
    query_embedding = embed_texts([question])[0]

    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        results = await retrieve_chunks(
            session=session,
            query_embedding=query_embedding,
            top_k=5,
            threshold=0.45,
        )

    assert isinstance(results, list)

    context = build_grounded_context(results)

    if results:
        assert context
        assert "Episode:" in context
        assert results[0].content[:50].strip() in context
    else:
        assert context == ""
