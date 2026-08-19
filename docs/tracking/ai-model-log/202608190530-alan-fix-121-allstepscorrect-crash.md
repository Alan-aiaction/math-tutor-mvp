# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Fixed a crash in my own previous fix (PR #121). Alan reported the practice
  screen crashing entirely (Next.js's generic error screen) when editing a checked step.
  Tried to find the actual error myself first rather than ask again: checked whether the
  frontend's real Sentry client-side error capture (`instrumentation-client.js`) was
  queryable - it isn't, no Sentry MCP tool connected this session - and checked Vercel's
  runtime-error tool as a fallback, which came back empty as expected (that only covers
  serverless/edge functions, not pure client-side exceptions). Root-caused instead by
  reading the exact merged code on `origin/master` directly (`git show`, not assumed):
  PR #121's `handleStepChange` fix changed `results` to potentially contain `null`
  entries mixed with real result objects, but `allStepsCorrect`'s `results.every((r) =>
  r.valid)` was never updated to guard against that per-entry case - only the
  whole-array-null case. Alan then supplied the actual console stack trace
  (`TypeError: Cannot read properties of null (reading 'valid')` at `Array.every`),
  which matched the code-reading diagnosis exactly.

  One-line fix: `results.every((r) => r && r.valid)`. `next build` clean, existing
  35-test suite unchanged and green. A real, honest example of a fix introducing a new
  bug alongside fixing the one it targeted - caught on the very next click-through pass,
  same session.
