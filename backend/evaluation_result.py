"""Builds the agreed EvaluationResult for a step (task #28).

The only place that constructs an EvaluationResult, so every future caller
gets a consistently-shaped object instead of hand-rolling one inline.
"""
from models import EvaluationResult


def build_evaluation_result(is_valid: bool, is_correct: bool, hint_text: str | None) -> EvaluationResult:
    """Compose the #25 (validity) and #26 (correctness) results into an
    EvaluationResult. A malformed step (is_valid=False) is always treated as
    incorrect regardless of is_correct.

    misconception_id is always None: the misconception-matching engine (#30)
    is 2nd-MVP scope, so there is no code path in 1st MVP that can populate
    it. #27's "needs review" signal is deliberately not consumed here either -
    EvaluationResult has no field for it; extending the agreed contract is a
    separate decision, not made in this ticket.
    """
    step_is_correct = is_valid and is_correct
    return EvaluationResult(
        valid=step_is_correct,
        misconception_id=None,
        hint_text=None if step_is_correct else hint_text,
    )
