"""Orchestration pipeline (task #36).

Wires the evaluator chain (#25-28) and #34's fallback hint into one callable
pipeline. Starts from already-recognized, already-confirmed Step.recognized_latex
- recognition (#19) is a separate, already-live step, not re-invoked here.

Does not call transition_validity.is_legal_transition() (#27): EvaluationResult
has nowhere to put that signal (see #28's own flagged gap), and calling it would
mean computing a value nothing consumes. Deferred, not solved here.
"""
from correctness_check import is_correct
from evaluation_result import build_evaluation_result
from expression_validity import is_valid_expression
from generic_hint import get_generic_hint
from latex_parser import LatexParseError, parse_math_latex
from models import EvaluationResult, Step


class PipelineError(Exception):
    """Raised when a step's evaluation fails for an unexpected reason - not a
    malformed student answer (handled as invalid) or a malformed correct_answer
    (a content bug that propagates as LatexParseError), but a genuine bug."""


def run_pipeline(steps: list[Step], correct_answer: str) -> list[EvaluationResult]:
    """Evaluate each step against correct_answer, returning one EvaluationResult
    per step, matching the already-built frontend's per-step ✓/⚠ display."""
    results = []
    for i, step in enumerate(steps):
        try:
            is_valid = False
            expr = None
            try:
                expr = parse_math_latex(step.recognized_latex)
            except LatexParseError:
                # Garbled student handwriting - a legitimate, expected outcome,
                # not a bug. Stays invalid; pipeline continues.
                pass
            else:
                is_valid = is_valid_expression(expr)

            correct = is_valid and is_correct(expr, correct_answer)
            hint = None if correct else get_generic_hint()
            results.append(build_evaluation_result(is_valid, correct, hint))
        except LatexParseError:
            raise
        except Exception as exc:
            raise PipelineError(f"Pipeline failed at step index {i}: {exc}") from exc
    return results
