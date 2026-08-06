# 2026-08-06 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: added `docs/tracking/decision-log.md` to `.gitignore` after
  repeated merge conflicts from multiple PRs editing entries near the same lines. Accepted
  tradeoff (discussed and confirmed with project lead): the file stops being shared via git
  going forward. Added a cutover note inside the file itself before gitignoring it, so any
  existing clone understands why it'll look frozen. Different fix than `ai-model-log.md`'s
  restructuring, since this file is edited in place over time (Proposed → Confirmed), not
  just appended to.
