# Design Decisions Log

Tracks product/architecture decisions made during development — what was decided, why, and
current status. Unlike `ai-model-log.md`, this is **not** append-only: a decision's `Status`
gets updated in place as team feedback arrives (Proposed → Confirmed / Revised /
Superseded), but the original reasoning stays visible rather than being deleted, so the log
stays a real record of how a decision evolved, not just a snapshot of the latest state.

Complements the "Open design gaps" tracker in
`docs/architecture/system-design.html#gaps`: that table says *what* needs deciding and *what
it blocks*; this log is *where the actual decision and reasoning get recorded* once made.

Entries are chronological (oldest first), matching `ai-model-log.md`'s convention — except
`[Living]` entries, which stay at the bottom regardless of date since they're continuously
refreshed rather than dated one-time decisions. A `[Living]` entry isn't a decision at all —
it's a standing view over the task board's current state (e.g. "what's next, in dependency
order"), kept here because it's derived reasoning worth having in one place, not because it's
a fact to trust blindly. Always carries a "Last verified" date; if that's gone stale, check
the actual board before trusting it.

---

## [Confirmed] Drop MyScript recognition confidence score (#21)

- **Date decided:** 2026-08-01
- **Status:** Confirmed — implemented
- **Affects:** #18 (Recognition Service), #19 (`POST /recognize`), #21 (superseded), #41
  (recognition preview)
- **Options considered:**
  - Threshold on a confidence score, only show Confirm/Edit below the threshold
  - Always show Confirm/Edit regardless of confidence
- **Decision:** Always show Confirm/Edit.
- **Reasoning:** MyScript's math recognition API doesn't return a confidence field at all
  (verified against the JIIX schema docs and a live test call), so there was nothing to
  threshold on. #41 already builds Confirm/Edit unconditionally for every recognized step,
  fully covering #21's original intent without a separate confidence-based implementation.
- **Team feedback:** Resolved by Jeff; confirmed on the task board 2026-08-01.

---

## [Confirmed] Ink capture built as a custom canvas, not MyScript's iink-ts SDK (#17)

- **Date decided:** 2026-08-01
- **Status:** Confirmed — implemented
- **Affects:** #17, #18/#19 (keeps MyScript keys server-side), #48
- **Options considered:**
  - MyScript's iink-ts web SDK (talks to MyScript's cloud directly from the browser)
  - Plain `<canvas>` + Pointer Events, capturing raw strokes and sending them to our own
    backend's `/recognize` endpoint
- **Decision:** Custom canvas capture.
- **Reasoning:** The iink-ts SDK would require exposing `MYSCRIPT_APP_KEY`/`MYSCRIPT_HMAC_KEY`
  client-side, which #48 (already Done) requires stay server-side only. Capturing raw
  strokes and sending them to our own `/recognize` keeps the keys on the backend, where
  `recognize_math()` (#18) already knows how to use them.
- **Team feedback:** n/a — implementation-level call, not sent for team review.

---

## [Confirmed] misconception_rules.escalation_hint_id left as an unenforced reference

- **Date decided:** 2026-08-03
- **Status:** Confirmed — implemented in `docs/architecture/database_schema.sql`
- **Affects:** #6 (schema), #9 (seed data), #30 (rule-matching engine)
- **Options considered:**
  - Enforce foreign keys in both directions between `misconception_rules` and `hints`
  - Enforce `hints.misconception_id` only; leave `escalation_hint_id` as a plain,
    unenforced reference
- **Decision:** The second option.
- **Reasoning:** Enforcing both directions creates an insert-order chicken-and-egg problem
  (can't insert a misconception's escalation hint before the hint row exists, can't insert
  the hint before the misconception row exists) for zero real benefit at seed-data scale
  (#9's data is small and controlled).
- **Team feedback:** n/a — design call within #6, not yet sent to the team.

---

## [Confirmed] Add Problem.solving_tip as a plain field, not a Hint

- **Date decided:** 2026-08-03
- **Status:** Confirmed — implemented in `docs/architecture/database_schema.sql` and
  `docs/architecture/api_contract_draft_20260728.md`
- **Affects:** #6 (schema), #12 (models), `docs/architecture/api_contract_draft_20260728.md`,
  #8 (seed content)
- **Options considered:**
  - Force per-problem strategy tips through Misconception/Hint via a synthetic per-problem
    "fake" misconception
  - Add a new nullable `Problem.solving_tip: str` field
- **Decision:** The new field.
- **Reasoning:** A `Hint` is reactive — keyed to a specific misconception, shown only after
  a matched wrong answer. The groep8 CSV's "Tip to Solve" column is proactive — authored
  once per problem, shown regardless of the student's answer. Forcing it through `Hint`
  would mean inventing a fake per-problem misconception, complicating #30's matching engine
  for no benefit; it belongs alongside `question_text`/`correct_answer` instead. Manual
  authoring for the pilot's ~20-30 seed problems isn't a scaling concern; longer-term, the
  plan is an AI-assisted authoring tool using the CSV's 64 rows as few-shot examples, with
  human review before seeding — noted as a future idea in the contract doc, not a ticket.
- **Team feedback:** n/a — decided directly with the project lead, not yet sent to the team.

---

## [Proposed] Problem.difficulty scale

- **Date proposed:** 2026-08-03
- **Status:** Proposed — sent to team, pending feedback
- **Affects:** `docs/architecture/api_contract_draft_20260728.md` (Problem model), `docs/architecture/database_schema.sql` (#6), seed content tagging (#8)
- **Options considered:**
  - Numeric scale (1-5)
  - Label (easy / medium / hard)
- **Decision:** Numeric 1-5, stored as a plain `integer` column.
- **Reasoning:** The tagging-ambiguity concern with a numeric scale ("is this a 2 or a 3?")
  is real, but the same ambiguity exists for labels ("is this easy or medium?") — both need
  a written rubric to be applied consistently, so that's not a real differentiator. Numeric
  wins on the criteria that don't have an easy workaround: a plain `integer` is simpler than
  a `text` + `CHECK`/enum, and it doesn't foreclose finer-grained sequencing later (e.g.
  1-5 → 1-10) without a breaking rename the way adding a 4th/5th label bucket would. Also
  zero rewrite from the current contract draft, which already has `difficulty: int`.
- **Team feedback:** _pending_ — #6's schema (`database_schema.sql`) and the contract doc
  proceed on this basis in the meantime, per project lead's explicit go-ahead 2026-08-03.

---

## [Confirmed] Test pyramid design + CI wiring deferred to 2nd MVP

- **Date decided:** 2026-08-04
- **Status:** Confirmed — deferred, not built
- **Affects:** All backend/frontend modules (full test-suite scope); no specific ticket yet
- **Options considered:**
  - Design the full 70/20/10 unit/integration/E2E test suite now and start implementing
    (backend route tests, frontend test tooling adoption, GitHub Actions CI)
  - Design it now for reference, but defer any implementation to 2nd MVP
- **Decision:** The second option. A full test-pyramid design was produced (unit/integration/
  E2E candidates across both backend and frontend, plus a GitHub Actions CI mapping — free for
  this public repo) and saved to `.claude/plans/test-pyramid-design.md` (local-only, per this
  repo's plan-file convention) for reference when the team picks this up.
- **Reasoning:** Not in scope for the 1st MVP — project lead's call. The design stays useful
  as-is once revisited: it already accounts for what exists today (backend pytest conventions,
  zero frontend test infra) and flags real open questions (frontend test tooling choice, a
  test-Supabase-project strategy for #14/#15) that'll need deciding whenever this is picked
  back up.
- **Team feedback:** n/a — decided directly with the project lead.

---

## [Proposed] Misconception.matching_rule format

- **Date proposed:** 2026-08-03
- **Status:** Proposed — sent to team, pending feedback
- **Affects:** `docs/architecture/api_contract_draft_20260728.md` (Misconception model),
  `docs/architecture/database_schema.sql` (#6, column type), #29 (define rule format), #30
  (rule-matching engine), #9 (seed misconception_rules)
- **Options considered:**
  - Regex matched against the canonical string form of the (wrong) expression
  - Structured comparison — a declarative rule matched against the parsed SymPy expression
    tree, not a string
- **Decision:** Structured comparison, stored as `jsonb` (not plain `text`).
- **Reasoning:** Regex's one real advantage — non-programmer authoring without a code
  change — is undercut by correctness risk (math expressions have many equivalent textual
  forms a regex can miss or over-match). Structured comparison builds directly on
  already-built, tested infrastructure (#22 parser, #23 canonical normalizer) instead of
  adding a parallel string-matching layer, and is more testable, matching this project's
  existing test style (#24, planned #52). Chose `jsonb` over plain `text` specifically for
  write-time validation — Postgres rejects malformed JSON on insert, catching a typo'd rule
  while seeding (#9) instead of it silently breaking later in Jeff's matching engine (#30).
  Not chosen for querying/indexing power — at #9's seed scale (5-10 rules) nothing queries
  into the JSON structure from SQL, so that upside doesn't apply yet.
- **Team feedback:** _pending_ — #6's schema (`database_schema.sql`) and the contract doc
  proceed on this basis in the meantime, per project lead's explicit go-ahead 2026-08-03.

---

## [Proposed] Misconception rule format (#29)

- **Date proposed:** 2026-08-03
- **Status:** Proposed — full spec at `docs/architecture/proposal_misconception_rule_format.md`, pending Jeff/Richard review per #29's own AC
- **Affects:** `docs/architecture/api_contract_draft_20260728.md` (Misconception model), #9 (seed data), #30 (rule-matching engine)
- **Options considered:**
  - Real-time LLM classification of each wrong answer (no pre-defined rule format needed at all)
  - A declarative JSON rule format (`operation`, `error_transform`, `check`), matched deterministically against the parsed expression tree
- **Decision:** The declarative format. AI scoped to two narrower places instead of the hot
  path: offline rule *authoring* (LLM drafts, human approves — same pattern as `solving_tip`),
  and an offline shadow-logging loop where unmatched wrong answers get logged for later
  human review, feeding future rule authoring.
- **Reasoning:** Real-time LLM-per-check was rejected — it breaks hint escalation (no stable
  `misconception_id` without deterministic matching), risks an incorrect or answer-revealing
  hint reaching a real child with no human review, adds per-request cost the README asks to
  minimize, adds latency to what should be immediate feedback, and isn't testable the way
  #26's "no false positives" AC requires. It would also re-litigate a call already made once
  for the adjacent hint-generation question (#34's board note: LLM generation deferred,
  "revisit before pilot"). The declarative format keeps matching fast, deterministic, and
  testable, while still using AI where it's genuinely safe and valuable — content creation
  and offline pattern-mining, not live judgment on a real student's answer.
- **Team feedback:** _pending_

---

## [Confirmed] Defer misconception-detection implementation to a 2nd MVP; pull shadow logging into the 1st

- **Date decided:** 2026-08-03
- **Status:** Confirmed — project lead's call, given 2026-08-22 MVP time pressure
- **Affects:** #29 (design proceeds now), #30/#9 (deferred), #25-28/#34 (stay in 1st MVP), #13/#15 (stay in 1st MVP), #63 (new ticket, makes the shadow log queryable), #61 (Post-MVP backlog item this now directly feeds)
- **Options considered:**
  - Defer the entire misconception/hint chain (#25-38) to 2nd MVP
  - Ship #25-28 (Evaluator) and #34 (generic fallback hint) in 1st MVP; defer only the
    misconception-specific layer (#30 matching engine, #9 real rule seeding) to 2nd MVP
- **Decision:** The second option, plus pulling shadow logging into 1st MVP rather than
  waiting for 2nd MVP.
- **Reasoning:** Deferring the whole chain would mean 1st MVP ships without any hint at all
  on a wrong answer, closer to a bare correctness-checker than the "diagnosing misconceptions
  and guiding with hints" tutor the README describes as the product's core value — risking a
  pilot that doesn't actually test the product's real differentiator. Splitting the defer to
  just the misconception-specific layer keeps a real (if generic) hint in front of students
  while deferring only the harder, evidence-hungry personalized-diagnosis part. Shadow
  logging's *storage* needs no new infrastructure — `attempt_steps` (#6/#7, live) already
  captures every wrong step once #13/#15 ship — but making that data actually queryable for
  review is real, separate work, given its own ticket (#63) rather than left implicit, so
  2nd MVP's rule set can be built from real groep 7/8 usage data instead of guesswork made
  under this MVP's time pressure.
- **Team feedback:** n/a — project lead scoping call, not yet sent to Jeff/Richard for review.

---

## [Confirmed] HTTPS enforcement relies on Railway/Vercel platform guarantee (#47)

- **Date decided:** 2026-08-05
- **Status:** Confirmed — verified, no code change
- **Affects:** `backend/main.py`, `backend/Procfile` (neither touched); deployment posture only
- **Options considered:**
  - Add app-level HTTPS enforcement (redirect middleware) as defense-in-depth
  - Rely on Railway/Vercel's platform-level HTTPS guarantee; verify it, don't add app code
- **Decision:** The second option — verify + document only.
- **Reasoning:** Railway terminates TLS at its edge and forwards plain HTTP internally to the
  container; a naive `HTTPSRedirectMiddleware` added inside the app risks a redirect loop
  unless the app is explicitly told to trust `X-Forwarded-Proto` (no `--proxy-headers` flag
  currently set). Taking on that risk isn't worth it for a gap live verification shows doesn't
  exist.
- **Verified (2026-08-05):** a plain `http://` request to the live Railway backend
  (`math-tutor-mvp-production.up.railway.app`) returns a `301` redirect to `https://`; a plain
  `http://` request to the live Vercel frontend (`math-tutor-mvp.vercel.app`) returns a `308`
  redirect to `https://`. Neither serves real content over plain HTTP — this is the actual "verify,
  don't assume" check the AC calls for, not an assumption from platform marketing claims.
- **Team feedback:** n/a — decided directly with the project lead.

---

## [Living] Full 1st MVP task order (dependency order, no owners, all statuses)

- **Last verified against the board:** 2026-08-04
- **Purpose:** every ticket needed for the 1st MVP pilot, in one dependency-ordered
  sequence — regardless of who owns it or its current status. Full detail (story, AC) stays
  on each ticket's own board card; this is the ordering layer only, not a duplicate.
- **Scope:** excludes #9/#30/#31/#33 (misconception-specific chain, deferred to 2nd MVP —
  see the scoping decision above), #21 (superseded), #60-62 (Post-MVP backlog).
- **Update trigger:** refresh whenever a listed ticket's status changes, or when PR #42
  (#29), #43 (#34/#63), or #33 (#8's owner) land — don't let this sit stale past that.

**Already done (17):** #1b, #6, #7, #11, #17, #18, #19, #22, #23, #24, #39, #40, #41, #42,
#43, #44, #48 — listed for completeness ("regardless of status"), not re-sequenced.

**Remaining, in dependency order:**

1. **#12** — Scaffold `backend/models.py`. Needs #11 (done).
2. **#8** — Seed problems. Needs #6 (done). Independent of everything else below.
3. **#13** — Supabase DB layer. Needs #6, #7 (done).
4. **#10** — Enable Supabase RLS (permissive baseline). Needs #7 (done).
5. **#25** — Expression validity check. Needs #22 (done).
6. **#47** — Enforce HTTPS everywhere. No real dependency, quick verification.
7. **#49** — Store LaTeX only. Needs #18 (done); full completion also needs #13/#15 (below).
8. **#29** — Rule format sign-off. Design already out (PR #42) — just needs Jeff/Richard
   review, not gated on #9 actually being seeded.
9. **#14** — `GET /problems/{id}`. Needs #12, #13, #8 (1, 3, 2 above).
10. **#15** — `POST /attempts`. Needs #12, #13 (1, 3).
11. **#16** — Error handling/logging. Needs #12, #13 (1, 3).
12. **#26** — Internal math correctness check. Needs #25 (5).
13. **#63** — Make shadow-logged wrong answers queryable. Needs #13, #15 (3, 10).
14. **#27** — Transition validity check. Needs #26 (12).
15. **#35** — Hint tone/language for the generic hint. Board still says `Depends on: #9` —
    **flagged, not yet fixed**, same issue #34 had: the one generic hint (#34) needs a tone
    decision regardless of real misconception content existing yet.
16. **#28** — Structured `EvaluationResult`. Needs #25, #26, #27 (5, 12, 14).
17. **#34** — Generic fallback hint. Needs #28 (16); already decoupled from #33/#9 (PR #43).
18. **#36** — Orchestration pipeline — **scope note:** simplified for 1st MVP, skips the
    misconception-detect step entirely (that's 2nd MVP). Needs #19 (done), #28, #34 (16, 17).
19. **#50** — Student access code. Frontend done; full tie-in needs #12/#13/#15 (1, 3, 10).
20. **#37** — Wire `POST /attempts/check` to the pipeline. Needs #36 (18).
21. **#38** — Pipeline timing/logging. Needs #36 (18).
22. **#51** — Tighten RLS with real access-code policies. Needs #50 (19).
23. **#56** — Deploy backend, connect Supabase. In progress; needs backend broadly done
    (through 21).
24. **#45** — Swap frontend mocks for real endpoints. Needs #19 (done), #37, #43 (done)
    (20).
25. **#52** — Unit tests: parser, evaluator — **scope note:** skip misconception-matcher
    tests, that piece is deferred. Needs #25-28 (5, 12, 14, 16).
26. **#53** — Integration tests: full `/attempts/check` pipeline. Needs #37 (20).
27. **#57** — Deploy frontend to Vercel (real app). Needs #45 (24).
28. **#46** — Test full flow live with Jeff. Needs #45 (24).
29. **#46b** — Network/error states in the UI. Needs #45 (24).
30. **#55** — Verify curriculum coverage vs. SLO tussendoelen. Needs #8 (2).
31. **#58** — Smoke-test production. Needs #56, #57 (23, 27).
32. **#59** — Monitoring/error logging (Sentry). Needs real code existing broadly — late,
    before real students touch it.
33. **#54** — Manual QA with real kids' handwriting. Needs #45 (24) + school access — this
    is effectively the pilot itself, last by design.

**Also flagged, not sequenced above:**
- **#20** (manual edit fallback) — no real blocking dependency, but its own board note
  already says it's likely fully covered by #41's existing Confirm/Edit. Probably a
  close-as-covered candidate rather than something to schedule — not resolved here, same as
  #35, left for a separate decision.
