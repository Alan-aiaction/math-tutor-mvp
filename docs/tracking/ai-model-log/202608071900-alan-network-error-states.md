# 2026-08-07 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: implemented #46b (network/error-state handling), built directly
  on top of #45's still-open branch (`feature/45-swap-mocks-for-real-api`) rather than waiting
  for it to merge, per explicit direction - will retarget this branch's base to `master` once
  #45 lands. New shared `frontend/app/lib/apiFetch.js` wraps both real fetch call sites
  (`StepBox.js`'s `/recognize`, `page.js`'s `/attempts/check`) with a 15s timeout via
  `AbortController` and consistent error mapping - also net-reduces duplication that already
  existed between the two call sites. Verified in isolation (no browser needed): a hanging
  server triggers the timeout at ~2020ms against a 2s limit with a retry-friendly message; a
  real 500 with backend-internal detail text in the body correctly shows a generic message
  instead, confirming nothing server-internal leaks to the student. `npm run build` clean.
