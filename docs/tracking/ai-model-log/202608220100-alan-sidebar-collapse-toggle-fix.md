# 2026-08-22 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Two bugs came in together from a screenshot: (1) the "+ Add next step"
  button stayed clickable after the answer was already correct, and (2) the sidebar's
  collapse toggle gave no visible cue how to un-collapse it. Investigated both before
  proposing fixes, per this repo's bug-fix discipline.

  Bug (1) turned into a real design question, not a quick fix: this app evaluates
  every "step" against the same final `correct_answer`, so a naive "disable once the
  last step is correct" fix (my first proposal) missed the actual reported case -
  Alan caught this directly by asking "what if intermediate step is correct," which
  exposed that steps behave like independent re-attempts, not sequential sub-steps.
  Alan parked this explicitly rather than let me patch the symptom - recorded in
  decision-log.md and in my own memory (`project_steps_workflow_design_parked.md`) so
  it isn't lost before the real design conversation happens.

  Bug (2) was scoped, confirmed, and fixed. Root cause went one layer past what was
  initially assumed: it wasn't just an unclear "☰" glyph - the logo box next to the
  toggle stayed mounted while collapsed (only its text hidden), competing with the
  toggle for space neither had at the collapsed `w-20` width. Fixed both: the toggle
  now shows a state-flipping chevron ("»"/"«", matching the `>>` Alan pointed at) with
  a matching dynamic aria-label, and the logo box is hidden entirely while collapsed
  instead of staying mounted and squeezed.

  TDD: new `AppShell.test.jsx` cases for the icon/label flip and the logo box's
  absence while collapsed. Full frontend suite green (62/62), `next build` clean. No
  browser/screenshot tool was available this session - said so directly rather than
  claiming a visual check that didn't happen.
