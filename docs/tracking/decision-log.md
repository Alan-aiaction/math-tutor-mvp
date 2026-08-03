# Design Decisions Log

Tracks product/architecture decisions made during development — what was decided, why, and
current status. Unlike `ai-model-log.md`, this is **not** append-only: a decision's `Status`
gets updated in place as team feedback arrives (Proposed → Confirmed / Revised /
Superseded), but the original reasoning stays visible rather than being deleted, so the log
stays a real record of how a decision evolved, not just a snapshot of the latest state.

Complements the "Open design gaps" tracker in
`docs/architecture/system-design.html#gaps`: that table says *what* needs deciding and *what
it blocks*; this log is *where the actual decision and reasoning get recorded* once made.

Entries are chronological (oldest first), matching `ai-model-log.md`'s convention.

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
- **Status:** Confirmed — part of the #6 schema plan, not yet implemented
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
- **Status:** Confirmed — part of the #6 schema plan, not yet implemented
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
- **Team feedback:** _pending_

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
- **Team feedback:** _pending_
