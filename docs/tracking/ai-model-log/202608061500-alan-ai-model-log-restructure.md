# 2026-08-06 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: restructured AI model tracking from one shared append-only
  table (`docs/tracking/ai-model-log.md`) to one file per session in
  `docs/tracking/ai-model-log/` — every PR editing that table's last rows caused repeated
  merge conflicts across this session's batch of parallel PRs (#42, #46-#52); two new files
  can never collide, so this removes the conflict source structurally. Old table frozen
  as historical record, not migrated. Updated `CLAUDE.md`'s "AI model tracking" section to
  match.
