# 2026-08-20 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Picked up the GDPR/AVG consent flow explicitly deferred on 2026-08-16 -
  Alan asked for a recommendation on what's next, I suggested this specifically because
  the 3rd MVP auth work it was waiting on (parent/child accounts, independent login,
  child dashboards) had just finished.

  Researched real reference products directly before designing anything, per this
  repo's own convention for exactly this kind of question - fetched Squla's and Junior
  Einstein's actual live privacy pages rather than assuming how a Dutch EdTech product
  handles parental consent. Found the real market norm is lighter than I'd have
  guessed: neither uses a consent checkbox or any parent-identity/age verification -
  consent is treated as implicit in a parent being the one who creates the account and
  each child's sub-account. Junior Einstein's own page confirms under-16s can't create
  their own account at all, which is exactly this app's existing model. This directly
  shaped scope: built a documented privacy statement + a consent notice at the actual
  moment of data collection (sign-up), and explicitly did *not* build parent
  ID-verification or a dedicated checkbox, since that would be above what either real
  product does - named as an explicit scope boundary in the plan, not silently skipped.

  New `/privacy` route (real Next.js page, reachable pre-auth), three link insertions
  (landing screen, sign-up notice, Account). Content is grounded in what's actually
  true in this codebase - cites the existing raw-ink-strokes-never-persisted invariant
  (task #49) as a real privacy-by-design fact already built, and documents the
  already-shipped hard-delete-a-child feature as the consent-withdrawal mechanism,
  rather than building anything new for that.

  Two real facts (contact email, Supabase hosting region) were needed from Alan - asked
  directly via AskUserQuestion rather than guessing or fabricating placeholder-looking
  real values. Alan deferred both ("later" / "not sure, check later"), so the page ships
  with clearly-marked bracketed placeholders `[privacy contact email - to be
  confirmed]` / `[to be confirmed by Alan]` instead of anything that could pass for a
  real value - flagged explicitly in the PR that this page isn't actually ready to go
  fully live until those two are filled in.

  TDD for the two new UI behaviors (ParentAuth shows the notice only in sign-up mode,
  Account links to /privacy). Frontend 48/48 (this branch is off master before PR #131
  merged, so the count doesn't yet include that PR's new tests), `next build` clean,
  `/privacy` compiles as its own static route. Checked
  docs/architecture/system-design.html directly per the new CLAUDE.md rule - confirmed
  nothing there describes privacy/consent, nothing needed updating.
