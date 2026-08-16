"""Orchestration pipeline (task #36, extended by #33).

Wires the evaluator chain (#25-28), #30's misconception matching + #33's hint
selection, and #34's fallback hint into one callable pipeline. Starts from
already-recognized, already-confirmed Step.recognized_latex - recognition (#19)
is a separate, already-live step, not re-invoked here.

question_text (the problem's own text, e.g. "6 x 199" - not correct_answer, see
misconception_matching.py's own docstring for why) is optional: callers that
don't have it (or existing tests that predate #33) get the pre-#33 behavior -
always the generic hint, misconception_id always None. Only when it's given, and
a step both parses and is wrong, does match_misconception() run at all - an
already-invalid/garbled step never had a parsed expr to match against.

Does not call transition_validity.is_legal_transition() (#27): EvaluationResult
has nowhere to put that signal (see #28's own flagged gap), and calling it would
mean computing a value nothing consumes. Deferred, not solved here.

Per-stage and total timing (task #38) uses this codebase's one existing logging
convention, established in db.py (#13): module-level logger, lazy %s formatting.
"""
import logging
import time
from contextlib import contextmanager

from correctness_check import is_correct
from evaluation_result import build_evaluation_result
from expression_validity import is_valid_expression
from hint_selection import select_hint
from latex_parser import LatexParseError, parse_math_latex
from misconception_matching import match_misconception
from models import EvaluationResult, Step

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """Raised when a step's evaluation fails for an unexpected reason - not a
    malformed student answer (handled as invalid) or a malformed correct_answer
    (a content bug that propagates as LatexParseError), but a genuine bug."""


@contextmanager
def _timed_stage(stage_name: str):
    """Log a stage's duration - not wrapped in try/finally, since a stage that
    raises is already handled (invalid input) or re-raised (PipelineError/
    LatexParseError) elsewhere; timing a failed stage isn't this ticket's goal."""
    start = time.perf_counter()
    yield
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("Stage '%s' took %.2fms", stage_name, duration_ms)


def run_pipeline(
    steps: list[Step], correct_answer: str, question_text: str | None = None
) -> list[EvaluationResult]:
    """Evaluate each step against correct_answer, returning one EvaluationResult
    per step, matching the already-built frontend's per-step ✓/⚠ display."""
    pipeline_start = time.perf_counter()
    results = []
    for i, step in enumerate(steps):
        try:
            is_valid = False
            expr = None
            try:
                with _timed_stage(f"parse (step {i})"):
                    expr = parse_math_latex(step.recognized_latex)
            except LatexParseError:
                # Garbled student handwriting - a legitimate, expected outcome,
                # not a bug. Stays invalid; pipeline continues.
                pass
            else:
                with _timed_stage(f"validate (step {i})"):
                    is_valid = is_valid_expression(expr)

            correct = False
            if is_valid:
                with _timed_stage(f"correctness (step {i})"):
                    correct = is_correct(expr, correct_answer)

            misconception_id = None
            if correct:
                hint = None
            else:
                if question_text is not None and expr is not None:
                    with _timed_stage(f"match_misconception (step {i})"):
                        misconception_id = match_misconception(question_text, expr)
                with _timed_stage(f"hint (step {i})"):
                    # select_hint(None) already falls back to the generic hint, so this
                    # covers both "no question_text given" and "no misconception matched"
                    # with the one call.
                    hint = select_hint(misconception_id)

            with _timed_stage(f"build_result (step {i})"):
                result = build_evaluation_result(is_valid, correct, hint, misconception_id)
            results.append(result)
        except LatexParseError:
            raise
        except Exception as exc:
            raise PipelineError(f"Pipeline failed at step index {i}: {exc}") from exc

    total_ms = (time.perf_counter() - pipeline_start) * 1000
    logger.info("Pipeline completed in %.2fms for %d step(s)", total_ms, len(steps))
    return results
