# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Two pieces of work this entry, discovered/done together.

  **Stacked-PR recovery.** Alan mentioned a PR had self-merged. Checked live rather than
  assuming - found PR #124 merged cleanly into `master`, but PR #125 and #126 (the rest
  of the independent-child-login stack) had merged into their *original* stale bases,
  not `master`, despite GitHub showing "Merged." Confirmed directly with `git show
  origin/master:<file>` for several PR2/PR3-specific symbols, all absent - not inferred
  from timestamps alone. Opened PR #127 directly from
  `feature/independent-child-login-frontend` (already containing both missing commits,
  correctly stacked on #124's real content) targeting `master`, verified conflict-free
  via a local dry-run merge first. No code changes, no re-review needed - purely a
  landing-location fix. Root cause this time: the retarget commitment was written into
  both PR descriptions, but the actual merges happened during a long conversation
  detour (browser automation, then CI questions) with no mechanism to notice a merge in
  real time absent being told - noted in decision-log.md as a real, unresolved gap, not
  papered over.

  **GitHub Actions CI.** Alan asked whether browser automation testing was possible
  (answered: yes via Playwright MCP, one command, `claude mcp add playwright -- npx -y
  @playwright/mcp@latest`, distinct from a permanent Playwright test suite which this
  repo's own Test Pyramid rule already gates behind asking first). That led to "can you
  auto-run tests via GitHub Actions" - confirmed with Alan that Actions secrets are
  private even on a public repo (never shown in the UI again once saved, redacted from
  logs, not exposed to outside-contributor PRs by default) before proceeding.

  This reopens a decision explicitly deferred on 2026-08-04 ("Test pyramid design + CI
  wiring deferred to 2nd MVP") - the original design (`.claude/plans/test-pyramid-design.md`)
  already worked out the right split, implemented exactly that: unit tests only
  (`pytest -k "not integration"`, `vitest run`, `next build`) on every PR, real-Supabase
  integration tests left manual/scheduled, not wired up. Found and fixed a real gotcha
  before shipping: `next build` fails with zero env vars at all, because
  `supabaseClient.js` constructs its client at module-eval time, not inside a function -
  reproduced locally, fixed with harmless dummy placeholder strings (not real secrets)
  inlined in the workflow file. End result: this PR needs zero GitHub secrets configured
  by Alan at all, revising what was said earlier in the conversation about needing them.

  Verified all three CI commands locally first, exactly as the workflow runs them,
  including a clean `npm ci` (not reusing already-installed node_modules) to catch any
  lockfile drift before CI would.
