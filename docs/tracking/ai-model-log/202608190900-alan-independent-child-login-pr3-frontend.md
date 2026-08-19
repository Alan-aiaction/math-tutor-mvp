# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** PR 3 of 3 (final) toward independent child login - the actual frontend
  flow. Builds on PR 2 (`POST /children/login` + `require_requester` - PR #125, still
  open, so this stacks on that branch, not `master`).

  Replaced `page.js`'s old unconditional `<ParentAuth/>` with a landing chooser
  ("Ik ben een ouder" / "Ik ben een kind") and a new `ChildLogin.jsx` component (family
  code + nickname + password, posts to the new backend endpoint). Child mode is a real
  third top-level render branch - checked before the parent-session check, so it works
  with zero parent session on the device at all - with no `AppShell`, just the practice
  session and a sign-out action. Stored under a deliberately separate localStorage key
  (`mathTutorChildSession`) from the existing parent-mediated `mathTutorActiveChild`.

  Extracted the Oefenen practice UI (ScratchPad/ProblemDisplay/StepList/button row) into
  a local `renderPractice()` closure inside `Home()` rather than duplicating it for
  child mode - both render branches call the same closure, no new component file since
  there's no reuse need outside `page.js` itself.

  TDD: `ChildLogin.test.jsx` written first (import failure, confirmed), then
  implemented.

  Went further than unit tests for verification here since this is the actual
  user-facing capability: started the local backend, created a real throwaway parent +
  child (not mocked), and drove the exact HTTP sequence a browser would through the
  running server - real family-code login, the returned token working on
  `/attempts/check`, a wrong password correctly 401ing, a mismatched `child_id`
  correctly 403ing, and `/parents/me` correctly 401ing with no token. Cleaned up the
  throwaway Supabase data afterward.

  Frontend 46/46 (up from 42), `next build` clean. Flagged to Alan that a real
  browser click-through is still worth doing once this merges - no browser automation
  connected this session, so the actual UI (landing chooser, form styling, sign-out
  button placement) hasn't been visually confirmed.
