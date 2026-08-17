# 2026-08-17 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Continuation of the same working session. Alan reported the live Vercel
  deployment showing "Network error" when adding a child after signing up/in. Root-caused
  directly by replaying the browser's own CORS preflight against the live Railway backend
  (not guessed): `backend/main.py`'s `CORSMiddleware` allowed only `Content-Type` in
  `allow_headers`, but ticket #76's parent/child auth (merged the previous day) requires
  every authenticated route to receive an `Authorization: Bearer <token>` header from the
  browser - never added to the CORS allowlist, so Railway rejected the preflight with
  `400 Disallowed CORS headers` and the browser silently blocked the real request. This
  broke every authenticated endpoint in production, not just "add child" - `/children`,
  `/attempts`, `/attempts/check`, and the just-shipped `/children/{id}/kpis` were all
  affected; sign-up/sign-in were unaffected since those go straight to Supabase Auth, never
  through this backend.

  Planned the fix (per this repo's bug-fix-discipline convention - root cause + proposed
  change presented and approved before writing code) and implemented it: added
  `"Authorization"` to `allow_headers`, plus a new regression test replaying the exact
  failing preflight against the app directly. Also flagged a second, separate issue found
  while investigating (sign-up confirmation emails link to `localhost:3000` instead of the
  production URL) - deliberately not bundled into this fix, per "fix one problem at a
  time."
