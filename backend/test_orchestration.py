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


def test_misconception_id_always_none():
    steps = [make_step(1, "5/7")]
    results = run_pipeline(steps, correct_answer="7/12")
    assert results[0].misconception_id is None
