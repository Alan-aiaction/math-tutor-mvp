# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Fixed "point 2" from the earlier priority list - sign-up confirmation emails
  linking to `localhost:3000` instead of production. Root cause had already been traced in
  an earlier session (`ParentAuth.jsx`'s `signUp()` call passes no `emailRedirectTo`, so
  Supabase falls back to the dashboard's Site URL, which was never updated off localhost) -
  confirmed directly against Supabase's own docs this session before writing the fix
  ("Change this from `http://localhost:3000` to your production URL... critical for email
  confirmations").

  Surfaced a genuine tool gap rather than working around it: none of the available
  Supabase MCP tools touch Auth's URL Configuration, so the fix is necessarily two-part -
  a code change (`emailRedirectTo: window.location.origin`, adapts per-environment rather
  than a hardcoded URL) plus a dashboard change (Site URL + Redirect URLs allow-list) that
  only Alan can make.

  TDD: extended `ParentAuth.test.jsx` with a failing assertion first (confirmed it failed
  against the un-fixed code - `signUp` called without `options` at all), then added the
  fix to make it pass. Frontend suite: 18/18 passing, `next build` clean.
