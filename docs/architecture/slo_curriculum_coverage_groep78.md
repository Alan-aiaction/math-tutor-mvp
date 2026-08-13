# SLO curriculum coverage check, groep 7/8 (ticket #55)

## What this is

Cross-checks all 47 seeded problems (`problems` table, sourced from `docs/content/
groep8_math_practice_en.csv` per ticket #8) against the official Dutch tussendoelen for
rekenen-wiskunde groep 7/8, published by SLO (Stichting Leerplanontwikkeling — the
national curriculum-development body). Source: *Tussendoelen rekenen-wiskunde voor het
primair onderwijs* (SLO, versie 2017), specifically the "eind groep 7," "eind groep 8,"
and "Concretisering van referentieniveau 1S" sections — archived at
`docs/content/slo-tussendoelen-rekenen-wiskunde-po-2017.pdf` so this check is reproducible
against the exact source used, not just this doc's summary of it.

## Methodology

Queried all 47 rows directly from the live `problems` table (`id`, `topic`, `difficulty`,
`question_text`, `correct_answer`), then matched each problem's actual mathematical
operation against SLO's domain/subdomain structure (GETALLEN, VERHOUDINGEN, METEN &
MEETKUNDE, VERBANDEN), not against the DB's own `topic` tags (`calculateInteger` /
`calculateMoney`) alone — those two tags collapse several genuinely different SLO
sub-goals into one label, so the real check required reading each problem's actual content.

## What's in the seed set

- **20 problems** (`calculateInteger`, ids 12–31): whole-number multiplication where one
  factor sits near a round number (`6 × 199`, `4 × 98`, `101 × 99`, `99 × 1001`, ...).
- **25 problems** (`calculateMoney`, ids 32–56): money multiplication, same near-round-number
  shape, in a euro context (`3 × €19.50`, `8 × €99.50`, ...).
- **1 problem** (id 57, `calculateInteger`): a word problem — division with a remainder
  ("Julia has 37 candies, shares with 7 friends, how many left over").
  **1 problem** (id 58, `calculateMoney`): a word problem — price-per-unit
  ("€6 for 800g of grapes, price per kilogram").

## Coverage against SLO

| SLO domain / subdomain | Covered? | Evidence |
|---|---|---|
| GETALLEN, Bewerkingen — vermenigvuldigen met hele getallen, "efficiënt... compenseren" strategy | **Well covered** | All 20 `calculateInteger` multiplication problems are textbook near-round-number compensation examples — directly matches SLO's own worked examples (groep 6: `12 x 99 = 12 x 100 - 12`; Concretisering 1S: `4 x 29 = 4 x 20 + 4 x 9 of 4 x 30 - 4`) |
| GETALLEN, Bewerkingen — vermenigvuldigen met decimale getallen (geld) | **Well covered** | All 25 `calculateMoney` problems directly match SLO's own example (groep 7: "3 tandenborstels van €2,25 per stuk") |
| GETALLEN, Bewerkingen — delen met rest | **Thinly covered** | 1 problem (id 57) matches SLO's "kan bij een deling in contexten de 'rest' interpreteren of verwerken" — a single example, not a depth of practice |
| METEN, Combinaties van grootheden — prijs per eenheid | **Thinly covered** | 1 problem (id 58) matches SLO's "prijs per kg" example directly — again, one example only |
| GETALLEN, Bewerkingen — optellen en aftrekken | **Not covered** | Zero addition/subtraction-only problems |
| GETALLEN, Bewerkingen — breuken (fraction arithmetic) | **Not covered** | Zero fraction problems — notably, this is the exact domain the misconception-rule proposal's own worked examples (fraction_addition/fraction_subtraction, ticket #30) target; there is currently no seeded problem that a fraction-related misconception rule could ever match against |
| GETALLEN, Getalbegrip — number sense (place value, number line, rounding, comparing) | **Not covered** | All seeded problems are "compute an answer" tasks, none test number sense directly |
| VERHOUDINGEN — ratios, percentages | **Not covered** | Zero ratio-table or percentage problems |
| METEN & MEETKUNDE, Meten — lengte/omtrek, oppervlakte, inhoud, gewicht, temperatuur, tijd (as primary topics) | **Not covered** | No dedicated problems beyond the one combined-grootheden example (id 58) |
| METEN & MEETKUNDE, Meetkunde — oriëntatie, construeren, vormen en figuren (geometry) | **Not covered** | Zero geometry content |
| VERBANDEN — tables, graphs, diagrams, number/figure patterns | **Not covered** | Zero data/graph-reading or pattern problems |
| Rekenen met de rekenmachine | **Not applicable to current format** | No calculator-use or estimation-as-check AC in the current problem shape |

## Summary

The seed set is narrow and deliberately deep on one skill, not broad across the
curriculum: it tests **multiplication with the compensation strategy, in both whole-number
and money contexts**, thoroughly and well — genuinely strong, textbook-aligned coverage of
that specific SLO sub-goal for groep 7/8. Everything else in the groep 7/8 tussendoelen —
addition/subtraction, fractions, ratios/percentages, most of meten (length, area, volume,
temperature, time), all of meetkunde (geometry), and verbanden (data/graphs) — has **zero
or only single-example coverage**.

This isn't a defect in what was built (ticket #8's own AC only ever targeted "20-30
problems... sourced from school context," not full curriculum breadth), but it is a real,
now-documented gap, per this ticket's own AC.

## Implication (not acted on here)

Expanding the seed set to cover these gaps would be new content work — explicitly out of
2nd MVP's declared scope ("Expanding the problem/question database... cut from this scope
entirely, not just deferred further," per the 2nd MVP board's Overview tab). This document
is the evidence base for that future decision, not a recommendation to act now. One
specific downstream implication worth flagging directly: ticket #30's rule-matching engine
is built and tested against the misconception-rule proposal's fraction examples, but with
zero fraction problems seeded, it currently has no real production content to ever match
against — a real, known limitation, not a bug (see `backend/misconception_matching.py`'s
own module docstring).

## Difficulty vs. curriculum level

The `difficulty` column (1–4, derived from complexity signals during seeding per ticket
#8) doesn't map onto SLO's groep 7 vs. groep 8 distinction — for the compensation-strategy
multiplication skill this set focuses on, SLO's groep 7 and groep 8 goals are nearly
identical in kind (both expect the strategy), differing mainly in the size of numbers
involved. All 47 problems use numbers well within both groups' expected ranges, so
`difficulty` here reflects perceived complexity, not a groep-7-vs-groep-8 curriculum
placement — worth knowing if `difficulty` is ever used to imply grade-level targeting.
