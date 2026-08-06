# 2026-08-06 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: resolved merge conflicts on PR #57 (#16) and PR #58 (#63) after
  Alan self-merged PRs #53-#59 in one batch; started #59 (Sentry error monitoring), backend
  half only. Wired `sentry_sdk.init()` into `backend/main.py` with `send_default_pii=False`
  (GDPR-for-minors stance) and explicit `capture_exception()` in the existing #16 catch-all
  handler. Found and fixed two non-obvious issues along the way: (1) a custom
  `exception_handler(Exception)` replaces Starlette's default middleware, so Sentry's
  auto-capture silently misses these exceptions unless reported explicitly; (2) Sentry's
  default logging integration turns every `logger.error()` call into its own event, which
  would have made already-handled errors (missing DB credentials, etc.) noisy production
  events too — disabled via `event_level=None` on `LoggingIntegration`, keeping the one
  explicit `capture_exception()` call as the sole event source. Verified live against the
  real DSN. Frontend (Next.js) half deferred until that Sentry project/DSN exists.
