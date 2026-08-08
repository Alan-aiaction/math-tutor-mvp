"""Fallback generic hint for wrong answers with no matched misconception (task #34).

Static for 1st MVP - AC #2 explicitly defers LLM-generation to later ("revisit
before pilot"). Kept behind a function, not a bare constant, so that swap can
happen later without touching any caller. Tone/wording refinement is #35's
job, not this ticket's - this just needs a real, non-answer-revealing Dutch
hint, per the agreed contract's "Language: Dutch only for MVP."

Task #35: wording drafted 2026-08-08, encouraging opener + "som" (kid-friendly
word for a math problem) instead of the more formal/textbook "berekening" -
targeting the 10-12yo audience per the ticket's own story. Draft, not final -
still needs Dev C's real review round before this counts as settled.
"""

_GENERIC_HINT_TEXT = (
    "Bijna goed! Kijk nog eens rustig naar je som, stap voor stap."
)


def get_generic_hint() -> str:
    """Return the static fallback hint shown when no specific misconception matched."""
    return _GENERIC_HINT_TEXT
