# 2026-08-20 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Grew directly out of the earlier Dashboard "view another child" request -
  talked through why that fix kept feeling awkward (clicking a name could never be
  fully safe while it might also silently reassign practice identity) and traced it
  back to `activeChild` doing two unrelated jobs at once. Walked through in
  conversation whether independent child login (already shipped) could fully replace
  it - confirmed technically yes, but only when the parent isn't already signed in,
  since the child-login option only appeared on the pre-session landing screen. Agreed
  direction: keep the existing tile-tap UX in Mijn kinderen exactly as-is, but change
  what it produces underneath - a real child session token, not `activeChild`.

  Backend: `POST /children/{child_id}/login` now issues a real token
  (`auth.issue_child_token`, reusing PR 2's mechanism) instead of a bare `Child`. One
  endpoint, one shape change - both login paths now converge on the same
  `{child, token}` session.

  Frontend: this was mostly deletion. `activeChild` state, its localStorage key,
  `selectChild`, the "no active child" fallback effect, the Oefenen nav item in
  `AppShell` (never reachable from inside the parent's shell anymore), and the
  topbar's child-identity pill all went away. `Dashboard.jsx` gained its own local
  `viewedChildId` state instead of taking `activeChild` as a prop - the original
  Dashboard ask fell out of this for free, since there's no practice-identity concept
  left for a click to accidentally disturb.

  Explicit tradeoff flagged rather than silently decided: left the backend's
  parent-token fallback path on `/attempts`/`/attempts/check` in place even though it's
  now unreachable from the frontend - removing it fully would mean rewriting most of
  `test_main.py`'s attempts-related test mocking for a lower-value cleanup, separable
  from the actual goal. Also named the real UX change plainly: a parent can no longer
  jump to Dashboard mid-practice-session without ending it first (same limitation
  independent login already had) - a second tab signed in separately covers it.

  TDD for the one genuinely new behavior (Dashboard's click-to-switch-viewed-child,
  written failing first). Everything else was updating existing tests to match
  deleted/renamed props, not new logic needing new tests. Beyond the mocked suites, ran
  two real end-to-end checks against a live local backend with a real throwaway
  parent+child - confirmed the modified parent-mediated login endpoint genuinely
  returns a working child token, and that token genuinely works on `/attempts/check`,
  not just asserted through mocks. Backend 289/289, frontend 45/45, `next build` clean.
