# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Closed a gap in PR #121's step-locking feature. Alan tested the just-merged
  PR #122 crash fix (confirmed: no crash), then found a real workflow gap: check step 1
  wrong, add step 2, and step 1 was still editable via Draw/Edit - even though the
  student had already moved on. PR #121 only locked a step once it was *correct*; an
  *incorrect* step stayed editable forever, which was intentional at the time (retry
  support for ticket #71/#72's hint escalation) but never accounted for editing after
  moving past a step.

  Fix: added an `isLast` signal (`index === steps.length - 1`, computed in
  `StepList.js`), passed to `StepBox.jsx`, changing the lock condition to
  `effectiveStatus !== "correct" && isLast` - a step is editable only while it's both
  not-yet-correct and still the current step. Confirmed this doesn't conflict with
  ticket #71/#72: retry always happens on the current step, before the next one is
  added, so that flow stays unlocked.

  TDD: `StepBox.jsx` had zero test coverage before this, so wrote `StepBox.test.jsx`
  first (failing against the old code, confirmed failing for the right reason), then
  implemented the fix. Needed to rename `StepBox.js` → `StepBox.jsx` and its dependency
  `InkCanvas.js` → `InkCanvas.jsx` to satisfy this repo's `.jsx`-for-tested-components
  convention (Vite's import-analysis needs the extension to parse JSX) - both plain
  renames, no behavior change. Full 39-test suite green, `next build` clean.
