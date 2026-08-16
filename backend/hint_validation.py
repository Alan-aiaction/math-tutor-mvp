"""Automated output-validation guardrails for live-generated hints (ticket #72, 2nd MVP).

Translates docs/architecture/llm_content_review_checklist.md's own automatable-check
table directly into code - see that doc's "Live escalation (#72)" section for the
per-criterion reasoning this mirrors:

| Criterion               | Automatable? | How                                          |
|--------------------------|--------------|-----------------------------------------------|
| No answer-revealing       | Yes          | length cap + correct_answer not a substring  |
| Dutch phrasing             | Yes          | heuristic common-word presence check          |
| Mathematical correctness   | No           | not checked here - the checklist doc already |
|                             |              | says this isn't automatable; #72's own AC's   |
|                             |              | "falls back to a static hint" is what covers  |
|                             |              | this gap, not a check in this module          |
| Encouraging tone            | Partially    | heuristic banned-flat-negative-opener list    |

Both heuristics (Dutch, tone) are deliberately simple word/prefix lists, not a real
NLP/language-detection library - honestly imperfect, matching the checklist's own
"Partially" framing for the tone check rather than overclaiming coverage. No new
dependency added for this.
"""
import re

MAX_HINT_LENGTH = 220

_COMMON_DUTCH_WORDS = {
    "je",
    "de",
    "het",
    "een",
    "is",
    "niet",
    "en",
    "naar",
    "voor",
    "dat",
    "je",
    "met",
    "nog",
    "eens",
    "kijk",
    "denk",
    "goed",
}

_BANNED_FLAT_NEGATIVE_OPENERS = ("fout", "nee", "verkeerd", "dat klopt niet")


def _looks_dutch(text: str) -> bool:
    words = set(re.findall(r"[a-zà-ÿ]+", text.lower()))
    return not words.isdisjoint(_COMMON_DUTCH_WORDS)


def _has_encouraging_opener(text: str) -> bool:
    stripped = text.strip().lower()
    return not stripped.startswith(_BANNED_FLAT_NEGATIVE_OPENERS)


def is_valid_hint(text: str, correct_answer: str) -> bool:
    """True if a live-generated hint clears every automatable guardrail.

    Mathematical correctness is NOT checked here (see module docstring) - callers
    must still treat this as a partial guarantee, not full safety, and fall back
    to the static generic hint on any exception from the LLM call itself, not just
    a False here.
    """
    if not text or not text.strip():
        return False
    if len(text) > MAX_HINT_LENGTH:
        return False
    if correct_answer in text:
        return False
    if not _looks_dutch(text):
        return False
    if not _has_encouraging_opener(text):
        return False
    return True
