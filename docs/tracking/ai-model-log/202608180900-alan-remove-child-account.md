# 2026-08-18 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Built the remove-child-account feature, requested after Alan asked "how to
  remove child account" and confirmed he meant a real feature, not a one-off manual
  cleanup. Confirmed directly (not assumed) that no delete capability existed anywhere -
  no function in `children.py`, no endpoint, no UI - and that neither FK
  (`attempts.child_id`, `attempt_steps.attempt_id`) has `on delete cascade`, so a naive
  delete would fail on any child with existing attempts. Presented hard-delete vs.
  soft-delete as a real tradeoff before building; Alan chose hard delete.

  Shipped: `children.delete_child()` (explicit ordered cascade, ownership-scoped in the
  query itself), `DELETE /children/{child_id}` endpoint, a small inline-confirm remove
  affordance in `ChildPicker.jsx`, and unit/integration/frontend tests throughout. Caught
  two things worth a second look before they became real bugs: the endpoint needed to
  return 200 with a body (not 204) because `apiFetch.js` always calls `res.json()`, and
  CORS `allow_methods` needed `"DELETE"` added - the exact same class of gap as the
  `Authorization`-header CORS bug fixed the day before, this time for methods.

  Real process incident, self-caught: the feature branch was accidentally created from a
  stale local `master` (a `git fetch` earlier only updated the remote-tracking ref, not
  local `master` itself), silently missing both the KPI data layer and the CORS fix.
  Caught before any commit or push, fixed by fast-forwarding local `master` properly and
  recreating the branch - full detail in the decision log.

  Full verification: backend 238 unit + 19 integration tests (zero regressions), frontend
  14 -> 17 tests, `next build` clean, and a real end-to-end manual check (real parent +
  child + attempt, confirmed both the 403-for-wrong-parent case and the real cascading
  delete) against the live local backend + Supabase, zero residue after.
