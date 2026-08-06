"""Fallback generic hint for wrong answers with no matched misconception (task #34).

Static for 1st MVP - AC #2 explicitly defers LLM-generation to later ("revisit
before pilot"). Kept behind a function, not a bare constant, so that swap can
happen later without touching any caller. Tone/wording refinement is #35's
job, not this ticket's - this just needs a real, non-answer-revealing Dutch
hint, per the agreed contract's "Language: Dutch only for MVP."
"""

_GENERIC_HINT_TEXT = (
    "Dat is nog niet helemaal goed. Bekijk je berekening nog eens rustig, stap voor stap."
)


def get_generic_hint() -> str:
    """Return the static fallback hint shown when no specific misconception matched."""
    return _GENERIC_HINT_TEXT
