# 2026-08-06 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: implemented #16 (error handling, validation, logging). Real
  finding: nothing in the app ever called `logging.basicConfig()` — `logger.info()` calls
  (db.py, orchestration.py) were silently dropped, `logger.error()` had no timestamp/structure.
  #38's pipeline-stage-duration logs were never actually visible until this ticket. Fixed with
  one root-logger `basicConfig()` call, inherited by every module automatically. Also added
  request-logging middleware and a global exception handler (verified it doesn't shadow
  `/recognize`'s existing `RecognitionError` → 502 mapping). 3 tests, full suite 56 passed.
  Manually verified live via a real uvicorn instance — confirmed an actual timestamped console
  log line, not just a mocked assertion.
