# 2026-08-06 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: implemented #37 (`POST /attempts/check`, wiring `main.py` to
  #36's existing `orchestration.run_pipeline()`). Note: #37 is Jeff's ticket per CLAUDE.md's
  team split - built at explicit direction, kept local (not pushed, no PR) pending Jeff being
  looped in. `LatexParseError` (malformed `correct_answer`) maps to 400; `PipelineError` is
  deliberately left uncaught, falling through to #16's existing global exception handler
  (logging + Sentry capture + clean 500) since it represents a genuine bug, not bad input.
  4 new tests in `test_main.py`, hitting the real endpoint with no mocking (pure computation,
  no I/O) - full suite 96 passed.
