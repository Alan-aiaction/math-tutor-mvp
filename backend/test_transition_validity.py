import pytest

from latex_parser import parse_math_latex
from transition_validity import is_legal_transition


@pytest.mark.parametrize(
    "step_a_latex,step_b_latex",
    [
        (r"\frac{1}{4} + \frac{1}{3}", r"\frac{3}{12} + \frac{4}{12}"),
        (r"\frac{3}{12} + \frac{4}{12}", "7/12"),
        # "Correct but unusual method" (AC #2) - a friendly-numbers compensation
        # strategy from the actual seed content (groep8_math_practice_en.csv):
        # "199 is close to 200. Calculate 6x200=1200, then subtract 6x1=6."
        (r"6*199", r"6*200 - 6*1"),
    ],
)
def test_value_preserving_transitions_are_legal(step_a_latex, step_b_latex):
    step_a = parse_math_latex(step_a_latex)
    step_b = parse_math_latex(step_b_latex)
    assert is_legal_transition(step_a, step_b) is True


@pytest.mark.parametrize(
    "step_a_latex,step_b_latex",
    [
        (r"\frac{1}{4} + \frac{1}{3}", "5/7"),
        (r"6*199", "1200"),
    ],
)
def test_value_changing_transitions_need_review(step_a_latex, step_b_latex):
    step_a = parse_math_latex(step_a_latex)
    step_b = parse_math_latex(step_b_latex)
    assert is_legal_transition(step_a, step_b) is False


def test_unexpected_exception_during_comparison_needs_review_not_raises():
    class ExplodesOnCompare:
        def __eq__(self, other):
            raise RuntimeError("boom")

        def is_number(self):
            raise RuntimeError("boom")

    assert is_legal_transition(ExplodesOnCompare(), ExplodesOnCompare()) is False
