# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** PR 2 of 3 toward independent child login - the actual login. Builds on PR 1
  (`parents` table, family code, child cap - PR #124, still open at the time this
  branched, so this is a stacked PR based on that branch, not `master`; needs
  retargeting to `master` the moment PR #124 merges, per this repo's stacked-PR rule).

  New `POST /children/login`: takes `family_code + nickname + password`, no parent
  Bearer token needed at all - resolves parent by family code, then child by nickname
  scoped to that parent, verifies the password against the existing bcrypt check, and on
  success issues a short-lived signed token (PyJWT, `CHILD_SESSION_SECRET`, ~24h expiry)
  the child's browser can use on later requests. This is a small app-owned token, not a
  second Supabase identity - keeps ticket #76's original call (no synthetic-email
  Supabase accounts for children) intact rather than reopening it.

  New `require_requester` dependency, applied only to `POST /attempts` and
  `POST /attempts/check` - the two endpoints an independent child's practice session
  actually needs. Tries the child token first (pure local signature check, no network
  round-trip) before falling back to the parent's Supabase token. A child token proves
  ownership by construction, so `/attempts` now trusts `payload.child_id` only if it
  matches the token's own child_id - 403 otherwise, tested explicitly (a child token
  can't post an attempt under a sibling's id). Everything else - `/children` CRUD,
  `/children/{id}/kpis`, the existing parent-mediated child-picker login - stays
  strictly parent-only, unchanged.

  TDD throughout: `auth.py`'s token issuance/verification, `parents.py`'s
  family-code lookup, and `children.py`'s nickname lookup were all written failing
  first (import errors, confirmed before implementing). Generated `CHILD_SESSION_SECRET`
  directly and added it to `backend/.env` locally - flagged to Alan (not printed in
  chat, per this repo's secrets discipline) that Railway's production env vars still
  need it added manually, since I don't have Railway dashboard access.

  Backend 289/289 (up from 268), including new integration tests against the real
  Supabase project exercising the full family_code -> parent -> child -> password
  lookup chain (the login endpoint itself stays unit-tested with mocks, matching this
  repo's existing convention for endpoint tests).
