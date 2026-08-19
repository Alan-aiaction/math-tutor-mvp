# 2026-08-19 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** PR 1 of 3 toward independent child login. Alan asked for three things: a
  child should be able to access the app without the parent's session, the parent still
  creates the child's account/password (unchanged), and a per-parent cap on child count
  since pricing will eventually differ by number of children. Researched the real
  current auth architecture first (`backend/auth.py`, `children.py`, `main.py`, the
  `children` migration) rather than assuming - confirmed only the parent has a real
  Supabase identity, child "login" today is just a password check gated behind the
  parent's own already-authenticated session, and this was a deliberate call at ticket
  #76 time (synthetic-email Supabase accounts for children were explicitly considered
  and rejected).

  Presented a decision table for the one real open question - how does an independent
  child identify themselves, given nicknames are only unique per-parent, not globally -
  and recommended a family code (new `parents` table) over global-unique nicknames or a
  search-all-candidates login, both of which had real downsides at scale. Plan approved,
  then staged into 3 PRs (schema+cap, backend session token, frontend flow) matching the
  earlier dashboard rollout's own pattern.

  This PR: new `parents` table (family_code, max_children default 3), lazy
  get-or-create so existing parents aren't broken, `GET /parents/me`, cap enforcement in
  `create_child`, Account UI showing the code with a copy button. TDD throughout - unit
  tests written first for `parents.py` and the cap-check, confirmed failing (module not
  found) before implementing; same for the new Account.jsx section. Applying the
  migration to the live Supabase project was blocked by auto mode's own safety
  classifier (a destructive DB action) - flagged this explicitly and got Alan's direct
  go-ahead before applying, per this project's own established precedent from ticket
  #76's migration.

  Caught `docs/architecture/system-design.html`'s ER diagram was stale beyond just this
  change - it had never been updated for ticket #76 at all (no `CHILDREN` entity,
  `ATTEMPTS` still showed the retired `student_id` field) - fixed what was needed to add
  `PARENTS` consistently, flagged the remaining pre-existing gaps rather than fixing
  everything in one pass. Backend 268/268, frontend 42/42, `next build` clean.
