# 2026-08-07 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: implemented #14 (Richard's ticket, done at Alan's explicit
  direction/permission, same basis as #8). `backend/problems.py` (`get_problem()`,
  `ProblemNotFoundError`) follows `attempts.py`'s established DB-module pattern; `main.py`'s
  new `GET /problems/{problem_id}` route maps not-found to 404, connection failure to 502.
  Unit tests mock the Supabase client (`test_problems.py`); integration tests hit the real,
  live project with a self-cleaning throwaway fixture (`test_problems_integration.py`) - full
  suite 96 passed. AC#3 verified for real: started the backend locally and curled 3 real
  problem ids from #8's live seeded data (12/13/14), all returned correct fields; a genuinely
  nonexistent id returned a clean 404.
