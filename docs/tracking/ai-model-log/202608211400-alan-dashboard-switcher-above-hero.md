# 2026-08-21 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Alan caught a real UX gap from his own click-through (two screenshots): the
  only way to switch which child's numbers show in the Dashboard hero was clicking a
  row in the "Overview per child" comparison table - which sits below the hero it
  controls, so the control was far from the content it affected.

  Added a second click-to-switch row directly above the hero (one button per child),
  reusing the exact same `viewedChildId` state the table's rows already set - both
  controls now drive identical state, kept the table itself completely unchanged per
  Alan's explicit "keep the overview as it is."

  Adding a second place each child's name renders broke an existing test's assumption
  (`screen.getByText("Noor")` became ambiguous once two elements had that text) -
  caught and fixed this as part of the same change by scoping that query to
  `within(table)`, rather than leaving a latent test fragility.

  TDD: 2 new cases written failing first. Frontend 54/54 (up from 49), `next build`
  clean.
