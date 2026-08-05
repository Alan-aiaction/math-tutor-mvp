"""Expression validity check for parsed math steps (task #25).

latex_parser.parse_math_latex (#22) already guarantees its output is parseable
and free of unknown symbols, but not that it's a sensible arithmetic answer.
This is a narrower, second gate on the already-parsed expression - not a
correctness check (#26) and not a multi-step check (#27).
"""
import sympy


def is_valid_expression(expr) -> bool:
    """True if a parsed SymPy expression is a well-formed arithmetic value.

    Rejects relational/boolean objects, nan, complex infinity, real infinities,
    and complex numbers with a nonzero imaginary part - none of these are
    sensible answers for grade 7-8 arithmetic. Never raises: any unexpected
    exception while checking is treated as invalid rather than escaping.
    """
    try:
        if isinstance(expr, (sympy.core.relational.Relational, sympy.logic.boolalg.BooleanAtom)):
            return False
        if expr in (sympy.nan, sympy.zoo, sympy.oo, -sympy.oo):
            return False
        if expr.is_complex and not expr.is_real:
            return False
        return True
    except Exception:
        return False
