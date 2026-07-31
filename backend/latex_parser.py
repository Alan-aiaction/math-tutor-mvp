"""LaTeX -> SymPy parsing for recognized math steps (task #22).

Wraps sympy's LaTeX parser and fixes a real bug in it: sympy parses an
integer directly adjacent to a \\frac (e.g. "2\\frac{1}{2}", a mixed number)
as something other than addition, giving 2/2 = 1 instead of the correct 2.5.
Verified empirically - see PR description for the test cases that exposed it.
"""
import re

from sympy.parsing.latex import LaTeXParsingError, parse_latex

MIXED_NUMBER_RE = re.compile(r"(-)?(\d+)(\\frac\{[^{}]+\}\{[^{}]+\})")


class LatexParseError(Exception):
    """Raised when recognized LaTeX can't be parsed into a SymPy expression."""


def _fix_mixed_numbers(latex: str) -> str:
    def repl(match: re.Match) -> str:
        sign, whole, frac = match.group(1), match.group(2), match.group(3)
        if sign:
            return f"-({whole}+{frac})"
        return f"({whole}+{frac})"

    return MIXED_NUMBER_RE.sub(repl, latex)


def parse_math_latex(latex: str):
    """Convert a recognized LaTeX string into a SymPy expression.

    Raises LatexParseError on malformed/unparseable input instead of letting
    sympy's exception (or any other) escape uncaught.
    """
    fixed = _fix_mixed_numbers(latex)
    try:
        expr = parse_latex(fixed)
    except LaTeXParsingError as exc:
        raise LatexParseError(f"Could not parse LaTeX {latex!r}: {exc}") from exc

    # This tutor covers grade 7-8 arithmetic, not algebra - sympy's LaTeX
    # parser doesn't reject nonsense input (e.g. plain words), it silently
    # treats unknown tokens as free-variable symbols instead. Any leftover
    # free symbols mean the input wasn't valid arithmetic.
    if expr.free_symbols:
        raise LatexParseError(
            f"LaTeX {latex!r} parsed to a non-numeric expression with unknown symbols: {expr.free_symbols}"
        )

    return expr
