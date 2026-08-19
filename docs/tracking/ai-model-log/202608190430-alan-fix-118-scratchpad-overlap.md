# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Fixed a real regression Alan found on his first actual browser look at the
  merged dashboard/shell work - the left ScratchPad panel rendered as a large blank box
  overlapping the new sidebar instead of in the page margin. Exactly the kind of bug unit
  tests and a clean build can't catch, since it's purely visual/positional - flagged
  honestly in the previous session's decision-log entry as still needing a real
  click-through, and it did.

  Root-caused directly: `ScratchPad.js` used `position: fixed` anchored to the viewport's
  edges, which was correct when the page had no persistent chrome, but collided with
  PR #118's new sidebar occupying that same edge. Fixed by switching to `position:
  absolute` inside a newly `relative` `<main>` in `AppShell.jsx` - tracks the content
  pane's real bounds at any sidebar width instead of the viewport's.

  Also directly answered a capability question mid-task: confirmed (searched, not
  assumed) that no browser automation tool is connected this session, and explained what
  connecting one (a Playwright-based MCP server) would take - a one-time setup step only
  Alan can do.

  Frontend suite: 35/35 unchanged (no test covers ScratchPad - its own correctness is
  visual only). `next build` clean. Stated plainly that the fix is structurally correct
  but not pixel-verified without browser automation - that confirmation is still Alan's.
