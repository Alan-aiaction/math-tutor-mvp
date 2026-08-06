# 2026-08-06 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: implemented #63 (shadow-logged wrong answers, queryable) — a
  Supabase view (`shadow_log_wrong_answers`) joining incorrect `attempt_steps` with their
  attempt and problem, plus `docs/architecture/shadow-log-review.md` documenting access for
  Jeff/Richard (deliberately not `decision-log.md`, which stopped being git-tracked as of PR
  #54). NOT marked Done on the task board yet — the Supabase MCP is disconnected this session,
  so the migration hasn't been applied/verified against the live database. Task board card set
  to "In progress" with a clear note on what's blocking closure.
