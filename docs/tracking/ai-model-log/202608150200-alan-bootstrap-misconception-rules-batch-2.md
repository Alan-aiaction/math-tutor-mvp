# 2026-08-15 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: ticket #9, batch 2. Feedback on the first drafted batch
  (docs/architecture/misconception_rules_bootstrap_batch_1.md, PR #102, merged) was that 3
  rules is too little.

  Added 4 more rules: one more misconception on the existing `multiplication_near_round`
  operation (wrong compensation direction/sign), a new `multiplication_double_near_round`
  operation + extractor covering the 2 "double compensation" problems (`101 × 99`,
  `99 × 1001`) batch 1 explicitly excluded, and two more on the existing
  `money_decimal_multiplication` operation (misplaced decimal point, rounds price before
  multiplying). Drafted total across both batches: 7 - written up in
  `docs/architecture/misconception_rules_bootstrap_batch_2.md`, same DRAFTED/NOT SEEDED
  status as batch 1.

  Investigated whether the 2 seeded word problems (division-with-remainder, price-per-kg)
  could also get rules. They can't with the current approach - every rule works by parsing
  `question_text` as a math expression, and word problems aren't one, and the `problems`
  table has no structured operand field. Weighed regex-per-sentence extraction vs. a schema
  migration vs. deferring; decided to defer (documented as a real, explicit gap in both the
  module docstring and the batch-2 doc) rather than force either a fragile hack or a
  migration for 2 rows.

  Also reformatted both batch docs' rule listings into tables (name, misconception, example,
  JSON), per direct request.

  PR #102 (batch 1) was self-merged mid-session - this batch's branch was started fresh off
  updated `master` rather than stacked on the now-merged branch, to avoid the stacked-PR
  merge-order trap CLAUDE.md warns about.

  Full backend suite: 145 → 156 tests, all green, zero regressions. Hand-verified each new
  rule template against real seeded problems before writing production code, including
  confirming none collides with any real seeded `correct_answer`.
