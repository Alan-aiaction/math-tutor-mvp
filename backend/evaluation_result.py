"""Builds the agreed EvaluationResult for a step (task #28, extended by #30/#33).

The only place that constructs an EvaluationResult, so every future caller
gets a consistently-shaped object instead of hand-rolling one inline.
"""
from models import EvaluationResult


def build_evaluation_result(
    is_valid: bool,
    is_correct: bool,
    hint_text: str | None,
    misconception_id: str | None = None,
) -> EvaluationResult:
    """Compose the #25 (validity) and #26 (correctness) results into an
    EvaluationResult. A malformed step (is_valid=False) is always treated as
    incorrect regardless of is_correct.

    misconception_id defaults to None (a correct step, or an invalid/unparseable
    one, never has one) - orchestration.py passes a real value once #30's matching
    engine finds one. #27's "needs review" signal is deliberately not consumed
    here either - EvaluationResult has no field for it; extending the agreed
    contract is a separate decision, not made in this ticket.
    """
    step_is_correct = is_valid and is_correct
    return EvaluationResult(
        valid=step_is_correct,
        misconception_id=None if step_is_correct else misconception_id,
        hint_text=None if step_is_correct else hint_text,
    )
