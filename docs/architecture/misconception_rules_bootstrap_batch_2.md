# Misconception rules — bootstrap batch 2 (ticket #9)

## Status: SEEDED (approved 2026-08-15)

Approved by the project lead ("consider it is approved for now") and inserted into the
live `misconception_rules` table on 2026-08-15, together with
[batch 1](misconception_rules_bootstrap_batch_1.md)'s 3 rules — 7 rows total.

## Why a batch 2

Feedback on batch 1 was that 3 rules is too little. This batch adds 4 more misconceptions
on the same two operations batch 1 already covers (`multiplication_near_round`,
`money_decimal_multiplication`), plus a new operation
(`multiplication_double_near_round`) that covers the 2 "double compensation" problems batch
1 explicitly excluded (`101 × 99`, `99 × 1001` — both factors near a round number, not just
one). Drafted content total across both batches: 7 rules.

## Can the 2 seeded word problems be covered too?

Investigated and deferred — worth recording why, since it's a real architectural question,
not an oversight.

The 2 word-problem-shaped seeded problems are:

- id 57: *"Julia has a bag with 37 licorice candies. She shares the candies with 7
  friends... How many candies are left over?"* (correct: 5 — needs knowing "Julia + 7
  friends" = 8 people)
- id 58: *"Anna pays €6 for a bunch of grapes. The bunch weighs 800 grams. How much do the
  grapes cost per kilogram?"* (correct: 7.50 — needs knowing 800g is 0.8 of a kg)

Every rule so far works by parsing `question_text` itself as a math expression and pulling
operands out of the resulting SymPy tree. The `problems` table has no structured field with
the numbers broken out (`id, topic, difficulty, question_text, correct_answer,
solving_tip` — checked `backend/models.py`'s `Problem` model too), so that approach can't
reach these 2 rows — the facts a solution needs ("8 people," "0.8 kg") live in the
sentence's *meaning*, not in its digits.

| | A — regex-pull numbers from `question_text` | B — add a structured operand field to `problems` | C — defer (this batch's choice) |
|---|---|---|---|
| **How** | Per-problem regex grabs the digits in the sentence, hardcode the "+1"/"÷1000" logic per wording pattern | Schema change: new column (e.g. `operands: jsonb`), rules read from it instead of parsing text | Leave the gap documented, build nothing this batch |
| **Pro** | No schema change | Generalizes to any future word problem, not just these 2 | No throwaway/premature code for a 2-problem case |
| **Con** | Doesn't generalize — pattern-matches English sentence structure, one hardcoded rule per wording; not really "extraction," more re-deriving the word problem's meaning in code | Touches `backend/models.py` (an agreed data model per `api_contract_draft`) — a real migration + backfill for 2 rows | The 2 word problems stay undiagnosed a while longer |

**Decision: C.** Neither a fragile per-sentence regex nor a schema migration is worth it for
2 rows. `misconception_matching.py`'s docstring already documents "word problems return
None, not a guess" as an expected limitation — this stays true a while longer. Revisit if
more word problems get seeded, or once a real reason to add structured operands exists
independent of this ticket.

## The rules

*(JSON is compact/single-line to fit a table cell — a real readability tradeoff for the
JSON column specifically. Can switch to a block-per-rule layout instead if that reads
better once you've seen this.)*

| Name | Misconception | Example | JSON |
|---|---|---|---|
| `multiplication_near_round_wrong_compensation_direction` | Correctly scales the compensation by the other factor, but adds it instead of subtracting it (or vice versa) — a sign confusion, distinct from batch 1's "forgot it entirely" and "used the raw diff." | `6 × 199` (correct: 1194) → student answers **1206** (`6×200 + 6×1` instead of `6×200 − 6×1`). | `{"id": "multiplication_near_round_wrong_compensation_direction", "topic": "multiplication", "description": "Scales the compensation correctly but adds it instead of subtracting it (or vice versa).", "matching_rule": {"operation": "multiplication_near_round", "error_transform": "wrong_compensation_sign", "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c + a*d"}}}` |
| `multiplication_double_near_round_forgot_both_adjustments` | For the "double compensation" shape where *both* factors are near a round number, rounds both and multiplies, forgetting both compensations — the natural extension of batch 1's "forgot adjustment" misconception to this case. | `101 × 99` (correct: 9999) → student answers **10000** (`100 × 100`). | `{"id": "multiplication_double_near_round_forgot_both_adjustments", "topic": "multiplication", "description": "Rounds both factors to round numbers and multiplies, forgetting both compensations.", "matching_rule": {"operation": "multiplication_double_near_round", "error_transform": "forgot_both_compensation_adjustments", "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c"}}}` |
| `money_multiplication_misplaced_decimal_point` | Multiplies as if the price were whole cents (e.g. treats `19.50` as `1950`), but doesn't shift the decimal point back afterward — a decimal-placement slip, distinct from batch 1's "drops the cents entirely." | `3 × €19.50` (correct: 58.50) → student answers **5850** (`3 × 1950`, decimal never restored). | `{"id": "money_multiplication_misplaced_decimal_point", "topic": "money", "description": "Multiplies as if the price were whole cents, but doesn't shift the decimal point back.", "matching_rule": {"operation": "money_decimal_multiplication", "error_transform": "misplaced_decimal_point", "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*b*100"}}}` |
| `money_multiplication_rounds_price_before_multiplying` | Rounds the price to the nearest euro first (round-half-up), then multiplies the rounded value — estimates instead of computing the exact decimal value. | `3 × €19.50` (correct: 58.50) → student answers **60** (rounds €19.50 → €20, then `3 × 20`). | `{"id": "money_multiplication_rounds_price_before_multiplying", "topic": "money", "description": "Rounds the price to the nearest euro first, then multiplies, instead of using the exact decimal value.", "matching_rule": {"operation": "money_decimal_multiplication", "error_transform": "rounded_price_before_multiplying", "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*floor(b + 1/2)"}}}` |

## Known, explicit limitation: no "compensated one side only" rule

For the double-compensation shape, a natural fourth misconception would be "compensates for
one factor's rounding but forgets the other" (as opposed to forgetting both). Not drafted:
`sympy.Mul.args` doesn't preserve written left-to-right order, and unlike the
`Add`-with-signs case in `_extract_two_fraction_operands` (batch 1), there's no sign here to
disambiguate which factor was "first" in the problem as written — so a rule about
compensating only one *specific* side can't be built without arbitrarily guessing which.
Named here as a real gap, not silently dropped.

## What these rules can and can't match

Verified against the real seeded problems (unit tests in
`backend/test_misconception_matching.py`), plus by hand that none of these 4 templates ever
equals the actual `correct_answer` for any real seeded problem it could apply to (so none
can spuriously fire against a correct answer):

- `wrong_compensation_direction` matches the same 18 of 20 `calculateInteger` problems batch
  1's two rules match (single-near-round-factor problems).
- `double_near_round_forgot_both_adjustments` matches exactly the 2 problems batch 1
  excludes (`101 × 99`, `99 × 1001`) — confirmed the existing single-factor rules still
  correctly don't fire on these 2 once this new rule is registered alongside them.
- Both money rules match the same 25 `calculateMoney` problems batch 1's rule matches.
- The 2 word-problem-style seeded problems still correctly return no match — see the
  decision table above.

## Seeded

Inserted directly into `misconception_rules` alongside batch 1's 3 rules — same row shape,
`escalation_hint_id` left `null`.
