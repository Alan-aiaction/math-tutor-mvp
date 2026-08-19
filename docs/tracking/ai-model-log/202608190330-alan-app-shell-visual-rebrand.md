# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** PR 2 of 3 for the dashboard/rebrand work - the app shell restructure and
  visual rebrand, building on PR 1's i18n/design-token foundation (merged). Replaced
  `page.js`'s old three-way full-screen branch (loading -> ParentAuth -> ChildPicker ->
  practice view, no persistent nav at all) with a real `AppShell` (collapsible sidebar,
  topbar) wrapping four nav destinations - Oefenen, Dashboard, Mijn kinderen, Account.
  Oefenen is real-state-driven, not a demo toggle: it's only rendered in the nav when
  `activeChild` is actually set, same rule the ouder-dashboard mockup demonstrated with a
  click-to-simulate switch. `ChildPicker` stopped being a forced full-screen gate and
  became the "Mijn kinderen" chapter's content instead - same component, same
  add/remove-child logic, just relocated; its own redundant sign-out button was removed
  since the shell's sidebar covers that globally now.

  TDD for the one genuinely new piece of logic: `AppShell.test.jsx` was written first
  (confirmed failing - module didn't exist), covering the nav-visibility rule specifically,
  before `AppShell.jsx` was built. The visual rebrand itself (swapping `emerald-700`/
  gray-X Tailwind classes for the new primary/warm/ink tokens across `ParentAuth`,
  `ChildPicker`, and the practice view) has no tests - no behavior for a test to drive.

  Deleted `ActiveChildHeader.jsx` and its test - dead code once its one job ("Working as:
  X" + "Switch child") moved into the shell's topbar, confirmed unused elsewhere before
  removing.

  Frontend suite: 22 -> 27 (net: +7 AppShell tests, -1 ChildPicker sign-out test now
  covered by AppShell, -2 ActiveChildHeader tests deleted with the dead component).
  `next build` clean. Dev-server check confirms the pre-auth screen boots correctly with
  the new fonts/lang attribute; the full authenticated shell flow (Oefenen visibility
  toggling live, colors across every screen) needs Alan's own click-through - no browser
  automation available to verify that end-to-end myself.
