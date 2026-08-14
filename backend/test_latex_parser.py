import pytest

from latex_parser import LatexParseError, parse_math_latex


@pytest.mark.parametrize(
    "latex,expected",
    [
        (r"\frac{1}{3} + \frac{1}{4}", 7 / 12),
        (r"2\frac{1}{2}", 2.5),
        (r"-2\frac{1}{2}", -2.5),
        (r"1 + 2\frac{1}{2}", 3.5),
        (r"0.75", 0.75),
        (r"-\frac{3}{4}", -0.75),
        (r"3 - 5", -2.0),
        ("6 × 199", 1194),
        ("3 × €19.50", 58.5),
        ("€9.50", 9.5),
    ],
)
def test_parses_expected_value(latex, expected):
    result = parse_math_latex(latex)
    assert float(result.evalf()) == pytest.approx(expected)


@pytest.mark.parametrize("latex", [r"\frac{1}{", "this is not latex math", r"\notacommand{x}"])
def test_malformed_latex_raises_clear_error(latex):
    with pytest.raises(LatexParseError):
        parse_math_latex(latex)
