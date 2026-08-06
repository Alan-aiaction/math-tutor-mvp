"""Transition validity check between consecutive steps (task #27).

For grade 7-8 arithmetic (not algebra with unknowns), there's no legitimate
reason for a step's value to change between consecutive steps - a legal
derivation is a value-preserving one (e.g. "1/4 + 1/3" -> "3/12 + 4/12",
same value, different form). So "legal" reduces to the same equivalence
check canonical_form already uses, applied step-to-step.
"""
from canonical_form import are_equivalent


def is_legal_transition(step_a_expr, step_b_expr) -> bool:
    """True only when step_b_expr is confirmed value-equivalent to step_a_expr.

    False means "needs review," not "confirmed illegal" - this never
    confidently declares a transition wrong, only whether it's confirmed
    legal. Any exception during comparison is caught and treated as
    needs-review too, rather than crashing.
    """
    try:
        return are_equivalent(step_a_expr, step_b_expr)
    except Exception:
        return False
