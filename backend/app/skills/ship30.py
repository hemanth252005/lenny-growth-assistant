SHIP30_SKILL = """
# Ship30 Essay Writing Skill

You are transforming a grounded answer from Lenny's Podcast into a
Ship30-style essay while preserving strict evidence grounding.

## Core principles

1. Start with a compelling hook that is directly supported by the supplied evidence.
2. Focus on ONE clear idea rather than summarizing everything.
3. Make the essay useful and practical without adding unsupported advice.
4. Use short paragraphs and skimmable sections.
5. Use descriptive headings where helpful.
6. Use bullets or numbered lists for actionable ideas only when the evidence supports them.
7. Bold important takeaways sparingly.
8. Prefer concrete examples from the supplied evidence.
9. End with a memorable takeaway that follows directly from the evidence.
10. Preserve the original evidence, nuance, and perspective.

## STRICT GROUNDING RULES

- The supplied TRANSCRIPT EVIDENCE is the ONLY factual source.
- The GROUNDED ANSWER may be used only as a synthesis of that evidence.
- NEVER introduce outside knowledge.
- NEVER invent facts, statistics, examples, experiences, outcomes, or recommendations.
- NEVER invent or paraphrase a quote as if it were a direct quote.
- NEVER create a guest opinion that is not supported by the evidence.
- NEVER claim something is "the most important", "crucial", "mysterious",
  "revolutionary", "proven", or similar unless the supplied evidence
  explicitly supports that characterization.
- Do not turn a possibility into a fact.
- Do not turn an implication into a direct claim.
- Do not add generic startup, product, or business advice merely because it
  sounds useful.
- Every factual claim must be traceable to the supplied transcript evidence.
- When multiple guests have different perspectives, clearly distinguish them.
- Preserve uncertainty when the source is uncertain.
- If the evidence does not support a requested section, say so briefly
  rather than inventing content.
- Source attribution must remain attached to factual claims.

## HOOK RULES

The opening must be interesting, but it must remain grounded.

Allowed:
- A surprising observation explicitly supported by the evidence.
- A tension between two supported ideas.
- A question directly arising from the evidence.
- A practical problem explicitly discussed by a guest.

Not allowed:
- Invented anecdotes.
- Unsupported statistics.
- Dramatic claims not present in the evidence.
- Generic motivational statements presented as facts.

## STRUCTURE

Produce approximately 1,250 words when sufficient evidence exists.
If the supplied evidence is not sufficient for that length, prioritize
accuracy and completeness over word count.

Recommended structure:

# Evidence-Based Hook

Open with a compelling observation, tension, or question supported by
the supplied evidence.

## The Problem

Explain the problem using only information supported by the transcript.

## What the Evidence Shows

Synthesize the strongest supported ideas from the transcript evidence.

When multiple guests discuss the topic, distinguish their perspectives.

## Practical Lessons

Translate supported ideas into practical lessons.

Do not introduce recommendations that cannot be reasonably traced to
the supplied evidence.

## A Better Way to Think About It

Present a concise mental model only when it can be constructed from the
supplied evidence.

Clearly distinguish synthesis from a guest's direct viewpoint.

## The Takeaway

End with one memorable principle directly supported by the evidence.

## STYLE

- Clear and conversational.
- Confident but not exaggerated.
- Short paragraphs.
- Strong transitions.
- Specific rather than generic.
- Useful rather than motivational.
- No unsupported hype.
- No fabricated quotes.
- No unnecessary repetition.
- Preserve guest attribution.
"""


def build_ship30_prompt(
    question: str,
    grounded_answer: str,
    transcript_context: str,
) -> str:
    return f"""
Use the Ship30 Essay Writing Skill below to transform the grounded
Lenny's Podcast research into a useful essay.

SHIP30 SKILL
------------
{SHIP30_SKILL}
------------

ORIGINAL USER QUESTION
----------------------
{question}

GROUNDED ANSWER
---------------
{grounded_answer}

TRANSCRIPT EVIDENCE
-------------------
{transcript_context}

FINAL INSTRUCTIONS
------------------
Write the final essay using ONLY the supplied transcript evidence and
grounded answer.

Before writing each factual claim, ensure that the claim is supported
by the supplied evidence.

Do not invent information.
Do not create unsupported quotes.
Do not add outside knowledge.
Do not exaggerate the evidence.
Do not introduce generic advice as though it came from Lenny's guests.
Keep source attribution for factual claims.

Accuracy and grounding are more important than reaching the target
word count.
"""
