# Misconception rules — bootstrap batch 1 (ticket #9)

## Status: DRAFTED, NOT SEEDED

Nothing in this document has been inserted into the live `misconception_rules` table.
This is a review artifact — the same "draft" state `draft_rule_from_note()` (ticket #69)
produces, just authored by hand instead of from a shadow-log note. Seeding requires an
explicit, separate approval on this specific content, matching this project's standing
principle that nothing an LLM (or, here, an AI assistant) drafts reaches
`misconception_rules` without a human sign-off.

## Why a bootstrap batch, not the usual shadow-log path

#9's normal path is: real wrong answers → #68's clustering → a human describes the
misconception → #69 drafts a structured rule → a human approves. That path currently has
no real data to work from — the `attempts`/`attempt_steps` tables were confirmed to
contain only development/testing data (yours and Jeff's, not real students) and were
cleared. The real pilot (#54) hasn't happened yet.

Rather than leave the entire misconception/hint chain (#9 → #70 → #33 → #71 → #72) blocked
indefinitely with no ETA, this batch is hand-authored from well-documented, common groep
7/8 arithmetic mistakes — not invented for this project, but recognizable, textbook-known
error patterns in exactly the operation types this project's own seed content covers
(confirmed via #55's curriculum coverage check: compensation-strategy multiplication and
money multiplication, the two dominant seeded problem types). This is an explicit,
documented deviation from #9's own AC ("sourced from #68's shadow-log review + #69's
drafting tool, not authored blind") — named here, not hidden. Ticket #61 ("expand
misconception rule library from real usage data") already exists for revisiting/correcting
these once real pilot data comes in.

## Prerequisite fix (already merged as part of this same PR)

Drafting these rules surfaced a real, separate bug: `latex_parser.parse_math_latex`
couldn't parse *any* of the 47 seeded problems' `question_text` — none of them are strict
LaTeX (they use a Unicode "×" and, for money problems, a "€" sign, neither of which sympy's
LaTeX parser understood). Fixed in `backend/latex_parser.py` (see that file's own docstring
and `decision-log.md` for the full writeup) — a genuine prerequisite for these rules to
match anything at all, not scope creep bundled in for convenience.

## The rules

*(JSON is compact/single-line so it fits a table cell — see the "more readable" note in
[batch 2's doc](misconception_rules_bootstrap_batch_2.md) if this format doesn't read well
in practice; happy to switch to a block-per-rule layout.)*

| Name | Misconception | Example | JSON |
|---|---|---|---|
| `multiplication_near_round_forgot_adjustment` | Uses the compensation strategy for multiplication near a round number (e.g. `6 × 199` as `6 × 200 − 6`), rounds and multiplies correctly, but forgets to subtract (or add) the compensation term back — treats the rounded multiplication as the final answer. | `6 × 199` (correct: 1194) → student answers **1200** (just `6 × 200`). | `{"id": "multiplication_near_round_forgot_adjustment", "topic": "multiplication", "description": "Rounds the messy factor to a round number and multiplies, but forgets to compensate back for the rounding.", "matching_rule": {"operation": "multiplication_near_round", "error_transform": "forgot_compensation_adjustment", "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c"}}}` |
| `multiplication_near_round_wrong_adjustment_amount` | Remembers to compensate, but subtracts (or adds) only the raw rounding difference, not that difference scaled by the other factor — e.g. for `6 × 199`, rounds to `6 × 200`, correctly notices 199 is 1 less than 200, but subtracts 1 instead of `6 × 1`. | `6 × 199` (correct: 1194) → student answers **1199** (`6×200 − 1`, should be `6×200 − 6×1`). | `{"id": "multiplication_near_round_wrong_adjustment_amount", "topic": "multiplication", "description": "Compensates by the raw rounding difference instead of that difference multiplied by the other factor.", "matching_rule": {"operation": "multiplication_near_round", "error_transform": "compensated_by_raw_diff_not_scaled_diff", "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c - d"}}}` |
| `money_multiplication_ignores_decimal_part` | When multiplying a whole number by a euro amount, multiplies only the whole-euro part and drops the cents entirely, rather than multiplying the full decimal value. | `3 × €19.50` (correct: 58.50) → student answers **57** (`3 × 19`, ignoring `.50`). | `{"id": "money_multiplication_ignores_decimal_part", "topic": "money", "description": "Multiplies only the whole-euro part of a decimal amount, drops the cents.", "matching_rule": {"operation": "money_decimal_multiplication", "error_transform": "dropped_decimal_part", "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*floor(b)"}}}` |

See [batch 2](misconception_rules_bootstrap_batch_2.md) for 4 more rules on these same two
operations, plus a new operation covering the "double compensation" problems this batch
excludes (below).

## What these rules can and can't match

Verified against the real seeded problems (unit + integration tests in
`backend/test_misconception_matching.py`):

- Match correctly against single-near-round-factor problems like `6 × 199`, `4 × 98`,
  `403`-style factors, etc. — 18 of the 20 seeded `calculateInteger` problems.
- **Explicitly do not match** the 2 "double compensation" problems (`101 × 99`, `99 × 1001`)
  where *both* factors are near a round number — the extractor requires exactly one messy
  factor, by design, rather than guessing which one to round. Noted as a real, known gap
  here, not silently mishandled — [batch 2](misconception_rules_bootstrap_batch_2.md) adds
  a rule that covers this case.
- Match correctly against integer-times-decimal money problems like `3 × €19.50` — the 25
  seeded `calculateMoney` problems.
- Still correctly return no match on the 2 word-problem-style seeded problems (division
  with remainder, price-per-unit) — neither is a two-factor product, so no extractor
  applies; this is expected, not a gap in these three rules specifically.

## More rules can follow

This is a first batch, not a claim of complete coverage — see
[batch 2](misconception_rules_bootstrap_batch_2.md), which adds 4 more rules on these same
two operations plus the double-compensation case. The 2 word-problem-style seeded problems
(division-with-remainder, price-per-unit) are still not covered by any batch so far — batch
2's doc explains why (their operands aren't recoverable from `question_text` alone) and lays
out the options for eventually closing that gap.

## Next step

Awaiting explicit approval on this content before anything is inserted into
`misconception_rules`. Once approved, seeding is a direct insert (same shape
`approve_and_seed_rule()` already uses) — no new code needed for that step.
