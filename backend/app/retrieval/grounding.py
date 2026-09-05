FALLBACK_MESSAGE = (
    "I do not have sufficient information in Lenny's podcast archive "
    "to answer this"
)


def has_sufficient_context(
    chunks,
) -> bool:
    return bool(chunks)
