import asyncio

from app.llm.factory import get_llm_provider


async def main():

    provider = get_llm_provider("ollama")

    response = await provider.generate(
        system_prompt=(
            "You are a helpful assistant. "
            "Answer briefly."
        ),
        user_prompt=(
            "Explain product-market fit in one sentence."
        ),
    )

    print()
    print("=" * 80)
    print("OLLAMA PROVIDER TEST")
    print("=" * 80)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
