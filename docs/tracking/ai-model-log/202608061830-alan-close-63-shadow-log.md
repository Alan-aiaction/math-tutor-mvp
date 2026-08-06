# 2026-08-06 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: closed out #63 (shadow-logged wrong answers, queryable) after
  the Supabase MCP reconnected. Applied the `shadow_log_wrong_answers` view migration, verified
  live with real throwaway data (one correct step, one incorrect step) — confirmed the view
  surfaces exactly the incorrect one with the right joined `question_text`/`correct_answer`,
  cleaned up with zero residue. Task board card and PR #58 updated to reflect full completion.
