import pytest

from latex_parser import parse_math_latex


@pytest.mark.parametrize(
    "latex,expected",
    [
        # Fractions
        (r"\frac{1}{3} + \frac{1}{4}", 7 / 12),
        (r"\frac{5}{8} - \frac{1}{4}", 3 / 8),
        # Mixed numbers
        (r"2\frac{1}{2}", 2.5),
        (r"1 + 2\frac{1}{2}", 3.5),
        # Decimals (standard point notation)
        (r"0.75", 0.75),
        (r"1.5 + 2.5", 4.0),
        # Dutch comma decimal notation
        (r"0,75", 0.75),
        (r"1,5 + 2,5", 4.0),
        # Negatives
        (r"-\frac{3}{4}", -0.75),
        (r"3 - 5", -2.0),
        (r"-2\frac{1}{2}", -2.5),
        # Implicit multiplication
        (r"2(1+3)", 8.0),
        (r"(1+2)(3+4)", 21.0),
    ],
)
def test_parses_expected_value(latex, expected):
    result = parse_math_latex(latex)
    assert float(result.evalf()) == pytest.approx(expected)
