import sympy
from sympy import Eq, I, oo

import pytest

from expression_validity import is_valid_expression
from latex_parser import parse_math_latex


@pytest.mark.parametrize(
    "latex",
    [
        r"\frac{1}{3} + \frac{1}{4}",
        r"2\frac{1}{2}",
        r"-2\frac{1}{2}",
        r"0.75",
        r"-\frac{3}{4}",
        r"3 - 5",
    ],
)
def test_valid_parsed_expressions_return_true(latex):
    assert is_valid_expression(parse_math_latex(latex)) is True


@pytest.mark.parametrize(
    "expr",
    [
        Eq(sympy.Integer(5), sympy.Integer(5)),
        sympy.true,
        sympy.nan,
        sympy.zoo,
        oo,
        -oo,
        sympy.Integer(2) + 3 * I,
    ],
)
def test_invalid_expressions_return_false(expr):
    assert is_valid_expression(expr) is False


def test_unexpected_exception_during_check_returns_false_not_raises():
    class ExplodesOnIsComplex:
        is_complex = property(lambda self: (_ for _ in ()).throw(RuntimeError("boom")))

    assert is_valid_expression(ExplodesOnIsComplex()) is False
