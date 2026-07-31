"""Canonical-form normalizer for parsed math expressions (task #23).

Parsed expressions from latex_parser.parse_math_latex stay unevaluated
(e.g. "1/4 + 1/3" doesn't auto-combine into "7/12"), and decimals (Float)
don't structurally equal the equivalent fraction (Rational) even after
that - so a plain `==` comparison treats mathematically identical answers
as different. normalize() forces full evaluation and converts decimals to
exact rationals so equivalent expressions compare equal.
"""
import sympy


def normalize(expr):
    """Return a canonical form of a SymPy expression: fully evaluated,
    with decimals converted to exact rationals."""
    return sympy.nsimplify(sympy.simplify(expr), rational=True)


def are_equivalent(expr_a, expr_b) -> bool:
    """True if two SymPy expressions represent the same value, regardless
    of how they were written (fraction order, decimal vs. fraction, etc)."""
    return normalize(expr_a) == normalize(expr_b)
