import pytest

from canonical_form import are_equivalent
from latex_parser import parse_math_latex


@pytest.mark.parametrize(
    "latex_a,latex_b",
    [
        (r"\frac{1}{3} + \frac{1}{4}", r"\frac{1}{4} + \frac{1}{3}"),
        (r"0.75", r"\frac{3}{4}"),
        (r"2\frac{1}{2}", r"\frac{5}{2}"),
        (r"-\frac{3}{4}", r"-0.75"),
        (r"\frac{1}{2} + \frac{1}{2}", r"1"),
    ],
)
def test_equivalent_forms_match(latex_a, latex_b):
    assert are_equivalent(parse_math_latex(latex_a), parse_math_latex(latex_b))


def test_different_values_do_not_match():
    assert not are_equivalent(parse_math_latex(r"\frac{1}{3}"), parse_math_latex(r"\frac{1}{4}"))
