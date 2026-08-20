# 2026-08-20 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Alan actually tested independent child login (family code -> practice
  screen) and caught a real regression I'd introduced: the child had no way to see
  their own progress. Traced it back to an early, genuinely-agreed requirement
  ("childer account should also has dashboard") that worked fine under the old
  parent-shared-shell design, then got silently dropped when independent login and
  "retire active child" collapsed child mode into a bare practice screen.

  Backend: `GET /children/{child_id}/kpis` switched from `require_parent_id` to
  `require_requester`, with the exact ownership-check shape `POST /attempts` already
  established - a child token only ever sees their own numbers, 403 on a sibling's id.

  Frontend: split rather than duplicated - extracted the hero/KPI/trend/weak-spots
  block out of `Dashboard.jsx` into a new `ProgressSummary.jsx` (pure `{child, kpis}`
  presentational component). `Dashboard.jsx` (parent, all children + comparison table)
  and new `MyProgress.jsx` (child, exactly their own data, no comparison table, no
  `GET /children` list call at all) both render it. Child mode gained a small nav of
  its own (Oefenen/Dashboard tabs) but deliberately not Mijn kinderen or Account - "same
  view as parent" scoped to content, not account management.

  TDD for `MyProgress.jsx`'s new fetch/loading/error logic, written failing first.
  `Dashboard.test.jsx` needed zero changes after the extraction - proof the refactor
  didn't alter any actual output. Backend 291/291, frontend 49/49, `next build` clean.
  Ran a real end-to-end check against a live local backend with a real throwaway parent
  + 2 children: one child's token fetched their own kpis and was correctly blocked
  (403) from a sibling's.

  Also the first task run under the new `CLAUDE.md` rule (added this same session,
  PR #130) requiring every plan to explicitly check `docs/architecture/` before being
  called done - checked directly, confirmed nothing there describes this endpoint or
  the dashboard flow, so nothing needed changing. Recorded the check happened, not just
  the absence of a diff.
