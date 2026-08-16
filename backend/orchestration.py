"""Orchestration pipeline (task #36, extended by #33 and #71).

Wires the evaluator chain (#25-28), #30's misconception matching + #33's hint
selection, #71's escalation trigger, and #34's fallback hint into one callable
pipeline. Starts from already-recognized, already-confirmed Step.recognized_latex
- recognition (#19) is a separate, already-live step, not re-invoked here.

question_text (the problem's own text, e.g. "6 x 199" - not correct_answer, see
misconception_matching.py's own docstring for why) is optional: callers that
don't have it (or existing tests that predate #33) get the pre-#33 behavior -
always the generic hint, misconception_id always None. Only when it's given, and
a step both parses and is wrong, does match_misconception() run at all - an
already-invalid/garbled step never had a parsed expr to match against.

previous_wrong_counts (ticket #71) is a parallel list to steps - how many times
this exact step has already come back wrong, across earlier checkWork() calls in
the same problem-solving session. Optional (default None -> all zeros), so every
pre-#71 caller/test is unaffected. Sourced from the frontend, not inferred from
persisted attempt history - see hint_escalation.py's own docstring and
decision-log.md for why (attempt_steps has no step-index column to correlate
against across separate historical rows).

INTERIM, until #72 lands (next PR in this stack): the escalated (level-2) hint's
TEXT still comes from #33's select_hint() pool, same as level 1 - only hint_level
actually differs. #72 replaces this call with a real live-generated hint on the
escalation path; #71 alone only needs the trigger + level to be correct, not the
content source.

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
from hint_escalation import should_escalate
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
    steps: list[Step],
    correct_answer: str,
    question_text: str | None = None,
    previous_wrong_counts: list[int] | None = None,
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
            hint_level = None
            if correct:
                hint = None
            else:
                if question_text is not None and expr is not None:
                    with _timed_stage(f"match_misconception (step {i})"):
                        misconception_id = match_misconception(question_text, expr)

                prior_count = (
                    previous_wrong_counts[i]
                    if previous_wrong_counts is not None and i < len(previous_wrong_counts)
                    else 0
                )
                hint_level = 2 if should_escalate(prior_count) else 1

                with _timed_stage(f"hint (step {i})"):
                    # select_hint(None) already falls back to the generic hint, so this
                    # covers both "no question_text given" and "no misconception matched"
                    # with the one call. INTERIM (see module docstring): the escalated
                    # path's hint TEXT still comes from this same pool call until #72
                    # lands - only hint_level actually differs for now.
                    hint = select_hint(misconception_id)

            with _timed_stage(f"build_result (step {i})"):
                result = build_evaluation_result(is_valid, correct, hint, misconception_id, hint_level)
            results.append(result)
        except LatexParseError:
            raise
        except Exception as exc:
            raise PipelineError(f"Pipeline failed at step index {i}: {exc}") from exc

    total_ms = (time.perf_counter() - pipeline_start) * 1000
    logger.info("Pipeline completed in %.2fms for %d step(s)", total_ms, len(steps))
    return results
