from unittest.mock import MagicMock, patch

import pytest

from generic_hint import get_generic_hint
from latex_parser import LatexParseError
from models import Step
from orchestration import run_pipeline


def make_step(step_id: int, recognized_latex: str) -> Step:
    return Step(id=step_id, attempt_id=1, recognized_latex=recognized_latex, is_correct=False)


def test_all_correct_multi_step_submission():
    steps = [
        make_step(1, r"\frac{1}{4} + \frac{1}{3}"),
        make_step(2, r"\frac{3}{12} + \frac{4}{12}"),
        make_step(3, "7/12"),
    ]
    results = run_pipeline(steps, correct_answer="7/12")
    assert len(results) == 3
    for result in results:
        assert result.valid is True
        assert result.hint_text is None


def test_incorrect_step_gets_generic_hint():
    steps = [make_step(1, "5/7")]
    results = run_pipeline(steps, correct_answer="7/12")
    assert results[0].valid is False
    assert results[0].hint_text == get_generic_hint()


def test_garbled_student_latex_is_invalid_not_a_crash():
    steps = [make_step(1, r"\notacommand{x}")]
    results = run_pipeline(steps, correct_answer="7/12")
    assert results[0].valid is False
    assert results[0].hint_text == get_generic_hint()


def test_malformed_correct_answer_propagates():
    steps = [make_step(1, "7/12")]
    with pytest.raises(LatexParseError):
        run_pipeline(steps, correct_answer=r"\notacommand{x}")


def test_empty_steps_returns_empty_list():
    assert run_pipeline([], correct_answer="7/12") == []


def test_misconception_id_stays_none_when_question_text_not_given():
    """Pre-#33 callers (or any caller with no question_text) get exactly the old
    behavior - misconception_id always None, no DB call made at all (select_hint
    short-circuits on misconception_id=None before ever touching Supabase)."""
    steps = [make_step(1, "5/7")]
    results = run_pipeline(steps, correct_answer="7/12")
    assert results[0].misconception_id is None
    assert results[0].hint_text == get_generic_hint()


def _mock_rules_client(rules):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = rules
    return mock_client


def _mock_hints_client(hints):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = (
        hints
    )
    return mock_client


_FORGOT_ADJUSTMENT_RULE = {
    "id": "multiplication_near_round_forgot_adjustment",
    "topic": "multiplication",
    "description": "Rounds the messy factor to a round number and multiplies, but forgets to compensate back.",
    "matching_rule": {
        "operation": "multiplication_near_round",
        "error_transform": "forgot_compensation_adjustment",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c"},
    },
    "escalation_hint_id": None,
}


def test_misconception_id_populated_when_question_text_given_and_matched():
    with (
        patch("misconception_matching.get_client", return_value=_mock_rules_client([_FORGOT_ADJUSTMENT_RULE])),
        patch("hint_selection.get_client", return_value=_mock_hints_client([])),
    ):
        steps = [make_step(1, "1200")]
        results = run_pipeline(steps, correct_answer="1194", question_text="6 × 199")
    assert results[0].misconception_id == "multiplication_near_round_forgot_adjustment"
    # No approved hint seeded yet for this misconception (mocked as empty) - falls
    # back to the generic hint, same honest state #9's batches left match_misconception
    # in before real content was approved.
    assert results[0].hint_text == get_generic_hint()


def test_selected_hint_used_when_an_approved_variant_exists():
    approved_hint = {
        "id": "multiplication_near_round_forgot_adjustment_hint_1",
        "misconception_id": "multiplication_near_round_forgot_adjustment",
        "text": "Bijna goed! Denk aan de correctie na het afronden.",
        "level": 1,
    }
    with (
        patch("misconception_matching.get_client", return_value=_mock_rules_client([_FORGOT_ADJUSTMENT_RULE])),
        patch("hint_selection.get_client", return_value=_mock_hints_client([approved_hint])),
    ):
        steps = [make_step(1, "1200")]
        results = run_pipeline(steps, correct_answer="1194", question_text="6 × 199")
    assert results[0].misconception_id == "multiplication_near_round_forgot_adjustment"
    assert results[0].hint_text == approved_hint["text"]


def test_no_misconception_match_falls_back_to_generic_hint_even_with_question_text():
    with (
        patch("misconception_matching.get_client", return_value=_mock_rules_client([])),
        patch("hint_selection.get_client", return_value=_mock_hints_client([])),
    ):
        steps = [make_step(1, "5/7")]
        results = run_pipeline(steps, correct_answer="7/12", question_text="1/3 + 1/4")
    assert results[0].misconception_id is None
    assert results[0].hint_text == get_generic_hint()


def test_garbled_step_never_attempts_misconception_matching():
    """An unparseable step has no expr to match against - matching must not even be
    attempted, regardless of question_text. Patches orchestration's own imported name
    (orchestration.py does `from misconception_matching import match_misconception`,
    so that's where the call is actually looked up, not the source module)."""
    with patch("orchestration.match_misconception") as mock_match:
        steps = [make_step(1, r"\notacommand{x}")]
        results = run_pipeline(steps, correct_answer="7/12", question_text="1/3 + 1/4")
    mock_match.assert_not_called()
    assert results[0].misconception_id is None


def test_logs_a_duration_for_each_pipeline_stage(caplog):
    steps = [make_step(1, "7/12")]
    with caplog.at_level("INFO", logger="orchestration"):
        run_pipeline(steps, correct_answer="7/12")
    stage_logs = [r for r in caplog.records if r.message.startswith("Stage '")]
    assert len(stage_logs) > 0
    assert any("took" in r.message for r in stage_logs)


def test_logs_total_pipeline_time(caplog):
    steps = [make_step(1, "7/12"), make_step(2, "5/7")]
    with caplog.at_level("INFO", logger="orchestration"):
        run_pipeline(steps, correct_answer="7/12")
    total_logs = [r for r in caplog.records if "Pipeline completed in" in r.message]
    assert len(total_logs) == 1
    assert "2 step(s)" in total_logs[0].message
