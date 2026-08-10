# 2026-08-10 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: bug fix for ticket #65, reported live - clicking "Next
  problem" showed a new problem but the previous step's recognised text stayed visible.
  Root cause: StepBox.js keeps its "Recognised as: ..." value in local state
  (useState(recognizedLatex)), initialized once and never re-synced to prop changes.
  page.js correctly resets the steps array, but StepList.js keyed each StepBox by index
  alone, so React reused the same instance instead of remounting it. Fix: key StepBox by
  `${problemId}-${index}` instead, so a new problem forces a real remount and clears all
  of StepBox's local state (recognised value, draft, drawing/editing mode, ink strokes),
  not just the lifted `steps` array. No behavior change for check/add/delete-step actions
  (problemId stays constant during those). Frontend production build verified clean.
