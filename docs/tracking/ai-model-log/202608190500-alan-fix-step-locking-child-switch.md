# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Fixed two more real bugs surfaced by Alan's first actual browser
  click-through of the practice flow - neither was a recent regression, both had existed
  since the practice UI was first built, just never actually exercised by a human before.

  Bug 1: a step marked correct had no "locked" state at all - `page.js`'s
  `addStep`/`deleteStep`/`handleStepChange` all wiped the *entire* `results` array
  instead of just the step that changed (so adding step 2 reset step 1's already-correct
  display), and `StepBox.js` never disabled Draw/Edit based on correctness (so a correct
  step stayed editable forever). Fixed both, deliberately leaving `checkWork()`'s
  full-array submission unchanged - once a step can't be edited, resubmitting it every
  time is harmless and avoids a much larger incremental-submission redesign for no real
  gain.

  Bug 2: switching to a different child left the previous child's in-progress steps on
  screen under the new child's name - `selectChild` never reset practice state. Fixed by
  having it call the already-existing `loadNextProblem()` (previously only wired to the
  "Next problem" button) instead of duplicating that reset logic.

  No new tests - `page.js`/`StepBox.js`/`StepList.js` have no existing coverage and both
  fixes are small, contained state changes. Verified by `next build` staying clean, the
  existing 35-test suite staying green, and a manual trace of each changed path. Same
  honest limitation as the last two fixes: not visually verified, no browser automation
  available this session - flagged that Bug 2 specifically needs a two-children
  click-through to actually confirm.
