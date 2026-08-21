"""Unit tests for hint_escalation_llm.py (ticket #72, extended for the per-account
lifetime LLM token limit).

Mocked llm.generate_text_with_usage() throughout - per the Overview tab's own testing
note, real LLM output isn't unit-testable for exact content. What's tested: the
validation-guardrail wiring and every fallback path, covering accept and reject cases
(missing config / network failure / validation rejection / token limit reached),
matching the Overview tab's explicit instruction for this exact ticket.
"""
from unittest.mock import patch

from generic_hint import get_generic_hint
from hint_escalation_llm import generate_escalated_hint
from llm import LLMError, LLMResponse

PARENT_ID = "11111111-1111-1111-1111-111111111111"

_ARGS = {
    "misconception_description": "Rounds the messy factor and forgets to compensate back.",
    "question_text": "6 × 199",
    "correct_answer": "1194",
    "wrong_answer_text": "1200",
}


def _usage(text, tokens_used=100):
    return LLMResponse(text=text, tokens_used=tokens_used)


def test_returns_generated_hint_when_valid():
    with patch(
        "hint_escalation_llm.generate_text_with_usage",
        return_value=_usage("Bijna goed! Denk aan de correctie."),
    ):
        result = generate_escalated_hint(**_ARGS)
    assert result == "Bijna goed! Denk aan de correctie."


def test_falls_back_to_generic_hint_on_llm_error():
    with patch(
        "hint_escalation_llm.generate_text_with_usage",
        side_effect=LLMError("LLM_API_KEY is not configured"),
    ):
        result = generate_escalated_hint(**_ARGS)
    assert result == get_generic_hint()


def test_falls_back_to_generic_hint_when_generated_text_fails_validation():
    """e.g. leaks the correct answer - a real, automatable rejection case."""
    with patch(
        "hint_escalation_llm.generate_text_with_usage",
        return_value=_usage("Het antwoord is 1194, dus reken opnieuw."),
    ):
        result = generate_escalated_hint(**_ARGS)
    assert result == get_generic_hint()


def test_falls_back_to_generic_hint_when_generated_text_is_not_dutch():
    with patch(
        "hint_escalation_llm.generate_text_with_usage", return_value=_usage("Almost there! Try again.")
    ):
        result = generate_escalated_hint(**_ARGS)
    assert result == get_generic_hint()


def test_falls_back_to_generic_hint_when_generated_text_is_empty():
    with patch("hint_escalation_llm.generate_text_with_usage", return_value=_usage("")):
        result = generate_escalated_hint(**_ARGS)
    assert result == get_generic_hint()


def test_works_without_a_misconception_description():
    """Escalation can still fire even when no misconception was matched - the
    prompt just frames it as a general 'stuck on this problem' case."""
    args = {**_ARGS, "misconception_description": None}
    with patch(
        "hint_escalation_llm.generate_text_with_usage",
        return_value=_usage("Bijna goed! Kijk nog eens rustig."),
    ):
        result = generate_escalated_hint(**args)
    assert result == "Bijna goed! Kijk nog eens rustig."


def test_generated_text_is_stripped_of_surrounding_whitespace():
    with patch(
        "hint_escalation_llm.generate_text_with_usage",
        return_value=_usage("  Bijna goed! Denk na.  \n"),
    ):
        result = generate_escalated_hint(**_ARGS)
    assert result == "Bijna goed! Denk na."


# --- Per-account lifetime LLM token limit ---


def test_no_parent_id_skips_the_limit_check_entirely():
    """Existing/test callers that don't pass parent_id (default None) behave exactly
    as before this feature - no DB touched at all."""
    with (
        patch("hint_escalation_llm.has_reached_llm_token_limit") as mock_check,
        patch(
            "hint_escalation_llm.generate_text_with_usage",
            return_value=_usage("Bijna goed! Denk aan de correctie."),
        ),
        patch("hint_escalation_llm.record_llm_tokens_used") as mock_record,
    ):
        result = generate_escalated_hint(**_ARGS, parent_id=None)

    assert result == "Bijna goed! Denk aan de correctie."
    mock_check.assert_not_called()
    mock_record.assert_not_called()


def test_falls_back_to_generic_hint_when_the_account_has_reached_its_token_limit():
    with (
        patch("hint_escalation_llm.has_reached_llm_token_limit", return_value=True),
        patch("hint_escalation_llm.generate_text_with_usage") as mock_generate,
    ):
        result = generate_escalated_hint(**_ARGS, parent_id=PARENT_ID)

    assert result == get_generic_hint()
    mock_generate.assert_not_called()  # never even attempts the paid call


def test_records_the_real_token_count_after_a_successful_live_hint():
    with (
        patch("hint_escalation_llm.has_reached_llm_token_limit", return_value=False),
        patch(
            "hint_escalation_llm.generate_text_with_usage",
            return_value=_usage("Bijna goed! Denk aan de correctie.", tokens_used=137),
        ),
        patch("hint_escalation_llm.record_llm_tokens_used") as mock_record,
    ):
        generate_escalated_hint(**_ARGS, parent_id=PARENT_ID)

    mock_record.assert_called_once_with(PARENT_ID, 137)


def test_still_records_usage_when_the_generated_hint_fails_validation():
    """The API call already happened and already cost real tokens by the time
    validation rejects its output - not counting it would let an account rack up
    unlimited validation-failing calls without the limit ever catching it."""
    with (
        patch("hint_escalation_llm.has_reached_llm_token_limit", return_value=False),
        patch(
            "hint_escalation_llm.generate_text_with_usage",
            return_value=_usage("Het antwoord is 1194, dus reken opnieuw.", tokens_used=90),
        ),
        patch("hint_escalation_llm.record_llm_tokens_used") as mock_record,
    ):
        result = generate_escalated_hint(**_ARGS, parent_id=PARENT_ID)

    assert result == get_generic_hint()
    mock_record.assert_called_once_with(PARENT_ID, 90)


def test_does_not_record_usage_when_the_llm_call_itself_fails():
    """An LLMError (missing config, network failure, timeout) means no successful
    response ever came back - nothing was actually spent, so nothing to record."""
    with (
        patch("hint_escalation_llm.has_reached_llm_token_limit", return_value=False),
        patch(
            "hint_escalation_llm.generate_text_with_usage",
            side_effect=LLMError("network error"),
        ),
        patch("hint_escalation_llm.record_llm_tokens_used") as mock_record,
    ):
        result = generate_escalated_hint(**_ARGS, parent_id=PARENT_ID)

    assert result == get_generic_hint()
    mock_record.assert_not_called()
