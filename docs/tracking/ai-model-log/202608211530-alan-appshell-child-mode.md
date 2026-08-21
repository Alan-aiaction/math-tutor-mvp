# 2026-08-21 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Part of a bundled 4-item request from Alan's own click-through screenshot
  (kids' layout, app rename, privacy page wording, a consent checkbox) - deliberately
  split rather than batched. This entry covers just the layout item; confirmed directly
  with Alan that "same layout as parent" meant (b) full navigation chrome (sidebar,
  more sections), not just visual polish - and specifically that Mijn kinderen/Account
  should stay out of a child's reach even though the chrome should match.

  `AppShell.jsx` (previously parent-only, hardcoded nav) became parametrized:
  `navItems` required prop, `showAccountLink` (default true), and `identityLabel` - the
  last one deliberately revives the *role* the old `activeChild`-driven topbar pill
  played before it was removed in the "retire active child" PR, without reintroducing
  `activeChild` itself - now driven by an explicit prop, used only for child mode's
  nickname display.

  `page.js`'s child-mode branch lost its own bespoke `<main>` markup entirely, now
  rendering through the exact same `<AppShell>` the parent path uses - a real
  simplification (one shell implementation, not two), not just a visual change.

  TDD: 4 new `AppShell.test.jsx` cases (custom navItems, showAccountLink hiding
  Account while keeping Uitloggen, identityLabel showing/not-showing) written failing
  first. Frontend 56/56 (up from 54), `next build` clean. Checked
  docs/architecture/system-design.html directly per the standing rule - confirmed
  nothing depicts the nav/shell structure, nothing needed updating.

  The other three items from Alan's same message (app rename to "Na de Bel" pending
  final confirmation, a "built by Alan" removal, and a real consent checkbox on
  ParentAuth) are still open, handled as separate work per this repo's "fix one problem
  at a time" convention - not bundled into this PR.
