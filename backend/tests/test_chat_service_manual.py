import asyncio

from app.database import AsyncSessionLocal
from app.services.chat_service import prepare_chat


async def main():
    question = (
        "How should a founder know when it is time "
        "to leave their job?"
    )

    async with AsyncSessionLocal() as session:
        answer, chunks, provider = await prepare_chat(
            session=session,
            question=question,
            provider="ollama",
        )

    print()
    print("=" * 80)
    print("END-TO-END CHAT SERVICE TEST")
    print("=" * 80)
    print(f"Question: {question}")
    print(f"Provider: {provider}")
    print(f"Retrieved chunks: {len(chunks)}")
    print()

    print("ANSWER:")
    print(answer)
    print()

    print("SOURCES:")
    for index, chunk in enumerate(chunks, start=1):
        print(
            f"[{index}] "
            f"{chunk.guest_name} | "
            f"{chunk.timestamp} | "
            f"{chunk.episode_title} | "
            f"similarity={chunk.similarity:.4f}"
        )


if __name__ == "__main__":
    asyncio.run(main())
