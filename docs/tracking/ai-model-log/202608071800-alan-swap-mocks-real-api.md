# 2026-08-07 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: implemented #45 (swap mocks for real backend endpoints).
  `/recognize` was already real (earlier ticket); the only remaining mock was
  `mockCheckWork()` (`mockCheck.js`, now deleted) - `page.js`'s `checkWork()` now calls the
  real `POST /attempts/check`. Found and fixed two real gaps along the way: (1) `StepBox.js`
  never reported its recognized/edited value back up to `page.js`, so the real check call
  would have sent stale initial data - added an `onChange` prop threaded through `StepList`;
  (2) `INITIAL_STEPS`' mock data used full `"lhs = rhs"` equation strings, which the real
  evaluator can't correctly check (confirmed live via curl - returned `invalid` for a step
  that should've been correct) - switched to plain single-expression values matching how
  `run_pipeline` actually works. `correct_answer` has no real source yet (no problem-selection
  UX exists) - added a `CORRECT_ANSWER` constant as a deliberate, minimal stopgap; real wiring
  is #14's separate frontend follow-up. Verified via curl with the exact payload shape
  `page.js` sends (correct/incorrect both behave correctly) and `npm run build`.
