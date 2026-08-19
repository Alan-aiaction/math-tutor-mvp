# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Started the real dashboard/shell/rebrand/i18n work (3rd MVP), building on the
  ouder-dashboard layout mockup from the previous session. Root-caused the current
  frontend's actual structure first (`page.js` is one component with three
  mutually-exclusive full-screen states, no persistent nav at all) before planning, then
  got explicit direction on three real architectural questions before writing code: full
  shell restructure (Dashboard reachable without picking a child first), full visual
  rebrand (not just the new screen), and real NL/EN support shipping in the live app now -
  which directly reverses a documented 1st-MVP non-goal ("Dutch only, per non-goals") in
  `docs/architecture/api_contract_draft_20260728.md`. Corrected that stale line and added a
  decision-log entry explaining why it no longer holds, rather than leaving the doc
  contradicting the new decision.

  Applied TDD for this ticket's logic-bearing pieces specifically (confirmed directly with
  the user after being asked): wrote `LanguageContext.test.jsx` first, watched it fail
  (module didn't exist), then built `LanguageContext.jsx`/`translations.js` to pass it.
  Pure visual work (the new `@theme` color/font tokens in `globals.css`, `next/font/google`
  wiring in `layout.js`) intentionally has no tests - there's no behavior for a test to
  drive there, and asserting a CSS class string would test implementation detail.

  Also caught a real process mistake before it repeated a third time: verified local
  `master` via `git merge-base HEAD origin/master` before branching (not just `git
  status`), which is exactly the check that was missing during the previous ticket's
  stale-branch incident - this time it caught local `master` two commits behind
  `origin/master` (PR #115 hadn't been fast-forwarded locally) and it got fixed before any
  work started on the new branch.

  Frontend suite: 17 -> 22 (new `LanguageContext.test.jsx`, 5 tests). `next build` and a
  manual dev-server check both clean.
