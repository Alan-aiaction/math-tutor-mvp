"""Unit tests for hint_escalation_llm.py (ticket #72).

Mocked llm.generate_text() throughout - per the Overview tab's own testing note,
real LLM output isn't unit-testable for exact content. What's tested: the
validation-guardrail wiring and every fallback path, covering accept and reject
cases (missing config / network failure / validation rejection), matching the
Overview tab's explicit instruction for this exact ticket.
"""
from unittest.mock import patch

from generic_hint import get_generic_hint
from hint_escalation_llm import generate_escalated_hint
from llm import LLMError

_ARGS = {
    "misconception_description": "Rounds the messy factor and forgets to compensate back.",
    "question_text": "6 × 199",
    "correct_answer": "1194",
    "wrong_answer_text": "1200",
}


def test_returns_generated_hint_when_valid():
    with patch("hint_escalation_llm.generate_text", return_value="Bijna goed! Denk aan de correctie."):
        result = generate_escalated_hint(**_ARGS)
    assert result == "Bijna goed! Denk aan de correctie."


def test_falls_back_to_generic_hint_on_llm_error():
    with patch("hint_escalation_llm.generate_text", side_effect=LLMError("LLM_API_KEY is not configured")):
        result = generate_escalated_hint(**_ARGS)
    assert result == get_generic_hint()


def test_falls_back_to_generic_hint_when_generated_text_fails_validation():
    """e.g. leaks the correct answer - a real, automatable rejection case."""
    with patch("hint_escalation_llm.generate_text", return_value="Het antwoord is 1194, dus reken opnieuw."):
        result = generate_escalated_hint(**_ARGS)
    assert result == get_generic_hint()


def test_falls_back_to_generic_hint_when_generated_text_is_not_dutch():
    with patch("hint_escalation_llm.generate_text", return_value="Almost there! Try again."):
        result = generate_escalated_hint(**_ARGS)
    assert result == get_generic_hint()


def test_falls_back_to_generic_hint_when_generated_text_is_empty():
    with patch("hint_escalation_llm.generate_text", return_value=""):
        result = generate_escalated_hint(**_ARGS)
    assert result == get_generic_hint()


def test_works_without_a_misconception_description():
    """Escalation can still fire even when no misconception was matched - the
    prompt just frames it as a general 'stuck on this problem' case."""
    args = {**_ARGS, "misconception_description": None}
    with patch("hint_escalation_llm.generate_text", return_value="Bijna goed! Kijk nog eens rustig."):
        result = generate_escalated_hint(**args)
    assert result == "Bijna goed! Kijk nog eens rustig."


def test_generated_text_is_stripped_of_surrounding_whitespace():
    with patch("hint_escalation_llm.generate_text", return_value="  Bijna goed! Denk na.  \n"):
        result = generate_escalated_hint(**_ARGS)
    assert result == "Bijna goed! Denk na."
