"""Live LLM hint-phrasing service, level-2 escalation only (ticket #72, 2nd MVP;
extended with a per-account lifetime token limit).

Only ever invoked via #71's escalation trigger (should_escalate() returning True) -
never on a first wrong answer, matching this ticket's own AC. Falls back to the
existing generic hint (#34) on ANY failure: a validation rejection
(hint_validation.is_valid_hint()), a missing LLM_API_KEY, a network error, a
timeout, or - as of this account-scoped limit - the account having already used up
its lifetime token budget. That's what makes this safe to ship before a real
LLM_API_KEY ever exists (none is configured in backend/.env today, see
decision-log.md) - same graceful-degradation spirit as orchestration.py's existing
garbled-LaTeX handling (bad input falls back, never crashes the pipeline).

parent_id is optional (default None) and, when given, gates the call on
parents.has_reached_llm_token_limit() and records real usage via
parents.record_llm_tokens_used() afterward - recorded even when the generated hint
later fails validation, since the API call itself already cost real tokens by then;
only skipped when the call itself never completed (LLMError). A caller that doesn't
pass parent_id (any pre-existing test, or any future caller with no account context)
gets the exact pre-limit behavior - no DB touched at all.

Deliberately not unit-tested against a real LLM response - per the Overview tab's
own testing note, LLM output isn't unit-testable for exact content. What's tested
here is the validation-guardrail wiring and the fallback behavior, both against a
mocked llm.generate_text_with_usage().
"""
import logging

from generic_hint import get_generic_hint
from hint_validation import is_valid_hint
from llm import LLMError, generate_text_with_usage
from parents import has_reached_llm_token_limit, record_llm_tokens_used

logger = logging.getLogger(__name__)

_MAX_TOKENS = 150


def _build_prompt(
    misconception_description: str | None,
    question_text: str,
    correct_answer: str,
    wrong_answer_text: str,
) -> str:
    misconception_context = (
        f"The student's specific mistake: {misconception_description}"
        if misconception_description
        else "The specific mistake isn't identified - the student is stuck on this problem generally."
    )
    return f"""You are writing a short, encouraging hint in Dutch for a groep 7-8 (10-12
year old) student who is stuck on a math problem, on their second wrong try at the
same step. Do not reveal the correct answer or make the next step trivially obvious -
nudge them toward noticing their own mistake.

Problem: {question_text}
The student's wrong answer: {wrong_answer_text}
{misconception_context}

Write ONE short sentence in Dutch (max {150} characters), starting with an encouraging
opener (e.g. "Bijna goed!", "Goed bezig!", "Kijk nog eens..."), age-appropriate for a
10-12 year old. Do not include the number {correct_answer} or restate the final answer.
Respond with ONLY the hint sentence - no prose, no quotes, no explanation."""


def generate_escalated_hint(
    misconception_description: str | None,
    question_text: str,
    correct_answer: str,
    wrong_answer_text: str,
    parent_id: str | None = None,
) -> str:
    """Return a live, validated, level-2 hint - or the static generic hint on any
    failure along the way, including the account having reached its lifetime LLM
    token limit (only checked when parent_id is given)."""
    if parent_id is not None and has_reached_llm_token_limit(parent_id):
        logger.info("Account %s has reached its LLM token limit, falling back to generic hint", parent_id)
        return get_generic_hint()

    try:
        prompt = _build_prompt(misconception_description, question_text, correct_answer, wrong_answer_text)
        response = generate_text_with_usage(prompt, max_tokens=_MAX_TOKENS)
    except LLMError as exc:
        logger.info("Live hint generation unavailable, falling back to generic hint: %s", exc)
        return get_generic_hint()

    if parent_id is not None:
        record_llm_tokens_used(parent_id, response.tokens_used)

    generated = response.text.strip()
    if not is_valid_hint(generated, correct_answer):
        logger.info("Live-generated hint failed validation, falling back to generic hint")
        return get_generic_hint()

    return generated
