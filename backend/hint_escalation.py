"""Hint escalation trigger (ticket #71, 2nd MVP).

Pure logic over a single input - no I/O, no mocking needed (matches the Overview
tab's own testing note for this exact ticket: "the detection/trigger logic, no
mocking, since it's pure logic over attempt state").

prior_wrong_count is sourced by orchestration.py from the caller (ultimately the
frontend, which tracks it client-side per step across checkWork() calls within the
same problem-solving session - see decision-log.md's write-up on why the backend
doesn't infer this from persisted attempt history instead: attempt_steps has no
step-index column today, so correlating "step 2 of this attempt" across separate
historical rows would mean assuming array-position stability rather than verifying
it).
"""

_ESCALATE_AT = 1


def should_escalate(prior_wrong_count: int) -> bool:
    """True once this step has already been wrong at least once before (i.e. the
    current check is the 2nd-or-later wrong try at this step) - triggers the
    level-2 path (#72) instead of repeating the level-1 pool hint (#33)."""
    return prior_wrong_count >= _ESCALATE_AT
