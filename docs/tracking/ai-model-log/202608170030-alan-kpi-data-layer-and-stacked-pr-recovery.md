# 2026-08-17 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Continuation of the same working session as the previous log entry
  (parent/child authentication, ticket #76). Covered, in order:

  Fixed a Vercel build failure on PR #110 (auth) — `Error: supabaseUrl is required` at
  Next.js prerender time, root-caused to `NEXT_PUBLIC_SUPABASE_URL`/
  `NEXT_PUBLIC_SUPABASE_ANON_KEY` existing only in local `.env.local`, never added to
  Vercel's own project environment variables (a separate configuration surface from local
  `next build`, which is why the build succeeded locally but not on Vercel).

  Discovered and fixed a real stacked-PR data-loss bug: PRs #106/#107/#108 showed
  "Merged" on GitHub but their code never reached `master`, because each had been merged
  into its own (already-merged) stacked base branch instead of being retargeted to
  `master` first. Recovered the missing code via a fresh PR (#112) rebuilt off current
  `master`, and — with Alan's explicit approval — made retargeting stacked PR bases
  Claude's own proactive responsibility going forward, codified into `CLAUDE.md` (PR
  #111), rather than relying on documentation alone.

  Resolved a genuine merge conflict on PR #110 (`backend/test_main.py`) combining two
  independently-built feature sets — parent/child auth and the hint-chain stack (tickets
  #70/#33/#71/#72) — after both had landed on `master` out from under the branch.

  Implemented the KPI data layer ticket (prerequisite for the 3rd MVP parent dashboard,
  not the dashboard UI itself): discovered via direct schema inspection that neither
  `attempts` nor `attempt_steps` had any timestamp column at all, making "accuracy trend
  over time" and "practice frequency" literally unbuildable — surfaced immediately, then
  planned and implemented the fix. New migration adds `attempts.created_at` and
  `attempt_steps.previous_wrong_count` (the latter persists a value `page.js` already
  computed for hint escalation, ticket #71's `wrongTryCounts`, previously discarded at
  save time). New `backend/kpis.py` with four aggregation functions (accuracy trend,
  practice frequency, average retries, weak-spot-by-topic), following this codebase's
  established "fetch raw rows via supabase-py, aggregate in plain Python" convention
  (`shadow_log_review.py`'s precedent) rather than raw SQL. New endpoint
  `GET /children/{child_id}/kpis`, auth + ownership checked the same way as the existing
  `/attempts` endpoint.

  Full backend suite: 185 -> 247, zero regressions. Manually verified end-to-end against
  the real local backend + live Supabase: real parent + child + two attempts with
  differing `previous_wrong_count`/`is_correct`, then a real authenticated
  `GET /children/{id}/kpis` call, confirmed all four computed values were correct. Zero
  residue in Supabase after (including a stray auth user left by a bug in the verification
  script itself, not application code — cleaned up separately).
