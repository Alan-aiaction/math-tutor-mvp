import pytest

from correctness_check import is_correct
from latex_parser import LatexParseError, parse_math_latex


@pytest.mark.parametrize(
    "submitted_latex,correct_answer",
    [
        (r"2/7", "8/28"),
        (r"4/28", "1/7"),
        (r"0.75", r"\frac{3}{4}"),
        (r"\frac{1}{4} + \frac{1}{3}", "7/12"),
        (r"3 - 5", "-2"),
        (r"-\frac{3}{4}", "-0.75"),
    ],
)
def test_equivalent_answers_are_correct(submitted_latex, correct_answer):
    submitted = parse_math_latex(submitted_latex)
    assert is_correct(submitted, correct_answer) is True


@pytest.mark.parametrize(
    "submitted_latex,correct_answer",
    [
        # AC's own example - 4/28 (=1/7) is a similar-looking but unequal fraction to
        # 2/7, guarding against exactly the false-positive AC #2 calls out.
        (r"2/7", "4/28"),
        (r"2/7", "3/28"),
        (r"0.75", "0.25"),
        (r"3 - 5", "2"),
    ],
)
def test_non_equivalent_answers_are_incorrect(submitted_latex, correct_answer):
    submitted = parse_math_latex(submitted_latex)
    assert is_correct(submitted, correct_answer) is False


def test_malformed_correct_answer_raises():
    submitted = parse_math_latex("2/7")
    with pytest.raises(LatexParseError):
        is_correct(submitted, r"\notacommand{x}")
