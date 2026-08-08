# 2026-08-08 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: investigated #51 (tighten RLS) before writing any SQL, and
  found the ticket's literal AC isn't achievable given the current architecture - the
  frontend never talks to Supabase directly (grepped, confirmed zero references), all DB
  access goes through the backend's `service_role` connection (bypasses RLS entirely), and
  the access code isn't a real Supabase identity (no auth session, no JWT, no `auth.uid()`
  to key a policy on). Writing RLS policies scoped to access code would have zero real
  effect - didn't do it, since that would be security theater, not real protection. Also
  found AC#2 already trivially holds: grepped `main.py`'s routes, confirmed no `GET
  /attempts` endpoint exists at all, so no code can read any attempt data through the app
  today, same honest "vacuously true" treatment #49 got. Documented the finding on the
  board and flagged the real trigger for revisiting this (the day a read endpoint for
  attempts gets built) instead of closing it with fake work.
