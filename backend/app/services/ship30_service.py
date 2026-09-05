from app.skills.ship30 import build_ship30_prompt
from app.llm.factory import get_llm_provider


async def generate_ship30_essay(
    question: str,
    grounded_answer: str,
    transcript_context: str,
    provider: str = "ollama",
) -> str:
    """
    Transform grounded Lenny research into a Ship30-style essay.

    The Ship30 writing principles are defined in the dedicated skill
    under app/skills/ship30.py.
    """

    prompt = build_ship30_prompt(
        question=question,
        grounded_answer=grounded_answer,
        transcript_context=transcript_context,
    )

    llm_provider = get_llm_provider(provider)

    return await llm_provider.generate(
        system_prompt=(
            "You are a professional essay writer following the supplied "
            "Ship30 Essay Writing Skill. "
            "Use ONLY the supplied grounded Lenny's Podcast evidence. "
            "Never invent facts, quotes, guests, statistics, or experiences."
        ),
        user_prompt=prompt,
    )
