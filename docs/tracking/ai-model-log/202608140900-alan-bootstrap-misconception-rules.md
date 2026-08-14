# 2026-08-14 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: ticket #9, bootstrap path. Confirmed live `attempts`/
  `attempt_steps` data (32 attempts, 47 steps) was development/testing residue (all blank
  `student_id`, heavy concentration on the old pre-#64 hardcoded `problem_id=12` default),
  not real student mistakes - confirmed directly by the project lead and cleared (0 rows
  remain in both tables).

  With no real shadow-log data, drafted a first misconception-rules batch from common,
  well-documented groep 7/8 mistakes instead of #9's usual shadow-log path - an explicit,
  documented deviation from #9's own AC, not a silent one.

  While designing which rules to draft, found and fixed a real prerequisite bug: none of
  the 47 seeded problems' `question_text` was parseable by the existing
  `latex_parser.parse_math_latex` (Unicode "×" and "€" weren't handled) - confirmed by
  direct test before touching any code, planned as its own decision (with pros/cons) per
  this repo's bug-fix discipline, then fixed alongside the rules work since both were
  discovered in the same investigation and the rules are meaningless without the fix.

  Extended `backend/misconception_matching.py` with two new operand extractors
  (`multiplication_near_round`, `money_decimal_multiplication`) targeting what's actually
  seeded (compensation-strategy multiplication, money multiplication) - the rule-format
  proposal's own fraction examples never matched real content (zero fraction problems
  seeded, per #55). Verified the rounding-detection logic by hand against every real
  seeded factor before writing production code, including correctly excluding the 2
  "double compensation" problems (`101 × 99`, `99 × 1001`).

  Three rules drafted, written up in
  `docs/architecture/misconception_rules_bootstrap_batch_1.md` - explicitly NOT seeded
  into the live `misconception_rules` table, awaiting separate explicit approval on the
  content itself, matching this project's human-approval-before-seeding principle.

  Full backend suite: 136 → 145 tests, all green, zero regressions (confirmed
  `test_orchestration.py::test_misconception_id_always_none` still holds). Zero residue in
  `misconception_rules` after integration tests.
