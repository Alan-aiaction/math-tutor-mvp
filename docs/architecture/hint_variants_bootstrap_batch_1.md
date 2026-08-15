# Hint variants — bootstrap batch 1 (ticket #70)

## Status: DRAFTED, NOT SEEDED

Nothing in this document has been inserted into the live `hints` table. Same review-artifact
status as the misconception-rules batches (`misconception_rules_bootstrap_batch_1.md` /
`_batch_2.md`) — seeding requires an explicit, separate approval on this specific content.

## Why hand-authored, not LLM-drafted

#70's own AC calls for an LLM to draft these via #67's abstraction. `LLM_API_KEY` isn't
configured in `backend/.env` (checked directly — no `LLM_*` vars present at all, though
`.env.example` documents them), and every LLM-touching ticket so far (#67, #69) has only
ever been exercised against a mocked provider — this repo has never made a real LLM call.
Rather than block the whole #70 → #33 → #71 → #72 chain on that missing key, you chose to
have these hand-authored directly instead ("your phrase is already claude LLM. good
enough") — an explicit, documented deviation from #70's AC, not a silent one, same spirit as
#9's bootstrap misconception-rules batches.

## What these are

2 hint variants for each of the 7 currently-seeded misconceptions (14 total), Dutch, groep
7-8 register, checked against #73's checklist
(`docs/architecture/llm_content_review_checklist.md`): no answer-revealing content,
age-appropriate phrasing, encouraging opener (varying `"Bijna goed!"` / `"Goed bezig!"` /
`"Goed geprobeerd!"` — all consistent with #35's confirmed `"Bijna goed!"` register, not a
single repeated sentence, per #70's own story: *"not the exact same sentence every time"*),
and factually tailored to what that specific misconception actually gets wrong, not a
generic "check your work."

All `level: 1` — these are the default, offline-approved pool (Overview tab's Decision C).
Level-2 hints come only from #72's live path, never this static pool.

## The hints

*(JSON compact/single-line, same tradeoff as the misconception-rules docs' tables.)*

| Hint ID | Misconception | Text | JSON |
|---|---|---|---|
| `multiplication_near_round_forgot_adjustment_hint_1` | forgot the compensation entirely | Bijna goed! Je hebt slim afgerond, maar vergeet niet om er daarna nog iets bij op te tellen of af te trekken. | `{"id": "multiplication_near_round_forgot_adjustment_hint_1", "misconception_id": "multiplication_near_round_forgot_adjustment", "text": "Bijna goed! Je hebt slim afgerond, maar vergeet niet om er daarna nog iets bij op te tellen of af te trekken.", "level": 1}` |
| `multiplication_near_round_forgot_adjustment_hint_2` | forgot the compensation entirely | Goed bezig! Reken eerst met het ronde getal, en doe daarna nog een stapje terug om bij het echte antwoord te komen. | `{"id": "multiplication_near_round_forgot_adjustment_hint_2", "misconception_id": "multiplication_near_round_forgot_adjustment", "text": "Goed bezig! Reken eerst met het ronde getal, en doe daarna nog een stapje terug om bij het echte antwoord te komen.", "level": 1}` |
| `multiplication_near_round_wrong_adjustment_amount_hint_1` | compensated by the raw difference, not scaled | Bijna goed! Je dacht aan de correctie - let op dat je het verschil net zo vaak meetelt als het andere getal aangeeft. | `{"id": "multiplication_near_round_wrong_adjustment_amount_hint_1", "misconception_id": "multiplication_near_round_wrong_adjustment_amount", "text": "Bijna goed! Je dacht aan de correctie - let op dat je het verschil net zo vaak meetelt als het andere getal aangeeft.", "level": 1}` |
| `multiplication_near_round_wrong_adjustment_amount_hint_2` | compensated by the raw difference, not scaled | Goed geprobeerd! Het stukje dat je terug moet rekenen, moet je vermenigvuldigen met het andere getal - niet los erbij doen. | `{"id": "multiplication_near_round_wrong_adjustment_amount_hint_2", "misconception_id": "multiplication_near_round_wrong_adjustment_amount", "text": "Goed geprobeerd! Het stukje dat je terug moet rekenen, moet je vermenigvuldigen met het andere getal - niet los erbij doen.", "level": 1}` |
| `multiplication_near_round_wrong_compensation_direction_hint_1` | compensated in the wrong direction | Bijna goed! Kijk nog eens goed: werd het getal dat je afrondde groter of kleiner? Daar hangt van af of je moet optellen of aftrekken. | `{"id": "multiplication_near_round_wrong_compensation_direction_hint_1", "misconception_id": "multiplication_near_round_wrong_compensation_direction", "text": "Bijna goed! Kijk nog eens goed: werd het getal dat je afrondde groter of kleiner? Daar hangt van af of je moet optellen of aftrekken.", "level": 1}` |
| `multiplication_near_round_wrong_compensation_direction_hint_2` | compensated in the wrong direction | Goed bezig! Check de richting van je correctie nog eens - je wilt terug naar het echte getal. | `{"id": "multiplication_near_round_wrong_compensation_direction_hint_2", "misconception_id": "multiplication_near_round_wrong_compensation_direction", "text": "Goed bezig! Check de richting van je correctie nog eens - je wilt terug naar het echte getal.", "level": 1}` |
| `multiplication_double_near_round_forgot_both_adjustments_hint_1` | forgot both compensations (double near-round) | Bijna goed! Je rondde allebei de getallen af - knap gezien! Nu moet je voor beide getallen nog een correctie doen, niet voor maar één. | `{"id": "multiplication_double_near_round_forgot_both_adjustments_hint_1", "misconception_id": "multiplication_double_near_round_forgot_both_adjustments", "text": "Bijna goed! Je rondde allebei de getallen af - knap gezien! Nu moet je voor beide getallen nog een correctie doen, niet voor maar één.", "level": 1}` |
| `multiplication_double_near_round_forgot_both_adjustments_hint_2` | forgot both compensations (double near-round) | Goed bezig! Met twee afgeronde getallen moet je ook twee keer een stapje terugrekenen. Ben je er eentje vergeten? | `{"id": "multiplication_double_near_round_forgot_both_adjustments_hint_2", "misconception_id": "multiplication_double_near_round_forgot_both_adjustments", "text": "Goed bezig! Met twee afgeronde getallen moet je ook twee keer een stapje terugrekenen. Ben je er eentje vergeten?", "level": 1}` |
| `money_multiplication_ignores_decimal_part_hint_1` | dropped the cents entirely | Bijna goed! Vergeet de centen niet - reken met het hele bedrag, ook het stukje achter de komma. | `{"id": "money_multiplication_ignores_decimal_part_hint_1", "misconception_id": "money_multiplication_ignores_decimal_part", "text": "Bijna goed! Vergeet de centen niet - reken met het hele bedrag, ook het stukje achter de komma.", "level": 1}` |
| `money_multiplication_ignores_decimal_part_hint_2` | dropped the cents entirely | Goed geprobeerd! Kijk nog eens naar de prijs: staat er ook iets na de komma? Dat hoort ook bij je berekening. | `{"id": "money_multiplication_ignores_decimal_part_hint_2", "misconception_id": "money_multiplication_ignores_decimal_part", "text": "Goed geprobeerd! Kijk nog eens naar de prijs: staat er ook iets na de komma? Dat hoort ook bij je berekening.", "level": 1}` |
| `money_multiplication_misplaced_decimal_point_hint_1` | multiplied as cents, never shifted the decimal back | Bijna goed! Je hebt goed gerekend - maar waar staat de komma nu in je antwoord? Kijk daar nog eens naar. | `{"id": "money_multiplication_misplaced_decimal_point_hint_1", "misconception_id": "money_multiplication_misplaced_decimal_point", "text": "Bijna goed! Je hebt goed gerekend - maar waar staat de komma nu in je antwoord? Kijk daar nog eens naar.", "level": 1}` |
| `money_multiplication_misplaced_decimal_point_hint_2` | multiplied as cents, never shifted the decimal back | Goed bezig! Als je met centen rekent, denk er dan aan om de komma aan het eind weer op de juiste plek te zetten. | `{"id": "money_multiplication_misplaced_decimal_point_hint_2", "misconception_id": "money_multiplication_misplaced_decimal_point", "text": "Goed bezig! Als je met centen rekent, denk er dan aan om de komma aan het eind weer op de juiste plek te zetten.", "level": 1}` |
| `money_multiplication_rounds_price_before_multiplying_hint_1` | rounded the price first instead of using the exact value | Bijna goed! Je rondde de prijs eerst af - handig om te schatten, maar reken nu met het echte bedrag voor het precieze antwoord. | `{"id": "money_multiplication_rounds_price_before_multiplying_hint_1", "misconception_id": "money_multiplication_rounds_price_before_multiplying", "text": "Bijna goed! Je rondde de prijs eerst af - handig om te schatten, maar reken nu met het echte bedrag voor het precieze antwoord.", "level": 1}` |
| `money_multiplication_rounds_price_before_multiplying_hint_2` | rounded the price first instead of using the exact value | Goed geprobeerd! Voor een schatting is afronden prima, maar dit sommetje vraagt om het exacte bedrag, met de centen erbij. | `{"id": "money_multiplication_rounds_price_before_multiplying_hint_2", "misconception_id": "money_multiplication_rounds_price_before_multiplying", "text": "Goed geprobeerd! Voor een schatting is afronden prima, maar dit sommetje vraagt om het exacte bedrag, met de centen erbij.", "level": 1}` |

## What #33 does with these before approval

`backend/hint_selection.py` (built as part of #33, same PR-stack) queries `hints` for
`level=1` rows matching a `misconception_id` and picks one at random. Until this batch is
approved and seeded, `hints` has 0 rows, so that selection always falls back to the existing
generic hint (#34) — same "code is real and ready, content isn't approved yet" state #9's
batches left `misconception_matching.py` in before #9 itself was seeded.

## Next step

Awaiting explicit approval on this content before anything is inserted into `hints` (same
gate as every batch so far).
