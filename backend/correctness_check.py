"""Internal math correctness check (task #26).

Compares an already-parsed, already-valid submitted expression against a
problem's correct_answer. Assumes validity was already checked by the caller
(expression_validity.is_valid_expression, task #25) - this only checks truth,
not well-formedness.
"""
from canonical_form import are_equivalent
from latex_parser import parse_math_latex


def is_correct(submitted_expr, correct_answer: str) -> bool:
    """True if submitted_expr is mathematically equivalent to correct_answer.

    correct_answer comes from curated seed content (task #8), not a student,
    so a malformed correct_answer is a content bug - parse_math_latex's
    LatexParseError propagates here rather than being swallowed.
    """
    correct_expr = parse_math_latex(correct_answer)
    return are_equivalent(submitted_expr, correct_expr)
