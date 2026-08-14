"""LaTeX -> SymPy parsing for recognized math steps (task #22).

Wraps sympy's LaTeX parser and fixes real gaps found via testing:
1. sympy parses an integer directly adjacent to a \\frac (e.g. "2\\frac{1}{2}",
   a mixed number) as something other than addition, giving 2/2 = 1 instead
   of the correct 2.5.
2. sympy doesn't understand Dutch-style decimal commas (e.g. "0,75"), which
   this tutor needs since it targets Dutch groep 7-8 students.
3. sympy's LaTeX parser doesn't understand the Unicode multiplication sign
   "×" (e.g. "6 × 199") - found while building the misconception-matching
   engine (ticket #9): every one of the 47 seeded problems' question_text
   uses "×", so without this fix question_text was unparseable for all of
   them, not just an edge case.
4. Likewise for the Euro sign "€" (e.g. "€19.50") - present in all 26
   calculateMoney-topic seeded problems. Stripped rather than translated:
   it carries no mathematical meaning, just a currency marker.
"""
import re

from sympy.parsing.latex import LaTeXParsingError, parse_latex

MIXED_NUMBER_RE = re.compile(r"(-)?(\d+)(\\frac\{[^{}]+\}\{[^{}]+\})")
DUTCH_DECIMAL_COMMA_RE = re.compile(r"(\d),(\d)")
MULTIPLICATION_SIGN_RE = re.compile(r"×")
CURRENCY_SYMBOL_RE = re.compile(r"€")


class LatexParseError(Exception):
    """Raised when recognized LaTeX can't be parsed into a SymPy expression."""


def _fix_mixed_numbers(latex: str) -> str:
    def repl(match: re.Match) -> str:
        sign, whole, frac = match.group(1), match.group(2), match.group(3)
        if sign:
            return f"-({whole}+{frac})"
        return f"({whole}+{frac})"

    return MIXED_NUMBER_RE.sub(repl, latex)


def _fix_dutch_decimal_commas(latex: str) -> str:
    return DUTCH_DECIMAL_COMMA_RE.sub(r"\1.\2", latex)


def _fix_multiplication_sign(latex: str) -> str:
    return MULTIPLICATION_SIGN_RE.sub("*", latex)


def _strip_currency_symbols(latex: str) -> str:
    return CURRENCY_SYMBOL_RE.sub("", latex)


def parse_math_latex(latex: str):
    """Convert a recognized LaTeX string into a SymPy expression.

    Raises LatexParseError on malformed/unparseable input instead of letting
    sympy's exception (or any other) escape uncaught.
    """
    fixed = _strip_currency_symbols(latex)
    fixed = _fix_multiplication_sign(fixed)
    fixed = _fix_dutch_decimal_commas(fixed)
    fixed = _fix_mixed_numbers(fixed)
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
