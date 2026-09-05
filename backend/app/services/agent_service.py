from claude_agent_sdk import ClaudeAgentOptions, query

from app.config import get_settings


AGENT_SYSTEM_PROMPT = """
You are The Lenny Growth Assistant.

You help users answer product, growth, leadership, and startup questions
using evidence from Lenny's Podcast transcript archive.

Grounding requirements:
- Use only transcript evidence supplied by the application.
- Never invent episode names, guests, timestamps, quotes, statistics, or claims.
- If the transcript evidence is insufficient, explicitly say so.
- When making factual claims, identify the relevant episode and timestamp.
- Synthesize evidence across multiple transcript excerpts when appropriate.
- Distinguish different guests' perspectives.
- Be concise and useful.
"""


async def run_claude_agent(
    question: str,
    transcript_context: str,
) -> str:
    """
    Run the Claude Agent SDK for a grounded Lenny response.

    Retrieval is performed by the application before the agent is called.
    Only the retrieved transcript evidence is supplied to the agent.
    """

    settings = get_settings()

    if not settings.anthropic_api_key:
        raise RuntimeError(
            "Anthropic API key is not configured. "
            "Set ANTHROPIC_API_KEY to use the Claude agent provider."
        )

    prompt = f"""
{AGENT_SYSTEM_PROMPT}

TRANSCRIPT EVIDENCE
===================
{transcript_context}

USER QUESTION
=============
{question}

Answer the user's question using ONLY the transcript evidence above.

Do not use outside knowledge.
Do not invent facts, quotes, guests, timestamps, statistics, or examples.
If the evidence is insufficient, explicitly say so.
"""

    options = ClaudeAgentOptions(
        model=settings.anthropic_model,
        system_prompt=AGENT_SYSTEM_PROMPT,
        max_turns=settings.agent_max_turns,
        permission_mode="bypassPermissions",
    )

    parts: list[str] = []

    async for message in query(
        prompt=prompt,
        options=options,
    ):
        content = getattr(message, "content", None)

        if not content:
            continue

        if isinstance(content, str):
            parts.append(content)
            continue

        for block in content:
            text = getattr(block, "text", None)

            if text:
                parts.append(text)

    answer = "".join(parts).strip()

    if not answer:
        raise RuntimeError(
            "Claude Agent SDK returned an empty response."
        )

    return answer