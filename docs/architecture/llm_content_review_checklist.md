# Human-review/approval checklist for LLM-drafted content (ticket #73)

## What this is

One consistent bar for anything an LLM drafts before it can reach a real student — applied
across every LLM-touching ticket in the 2nd MVP misconception/hint chain, instead of each
ticket inventing its own ad hoc standard.

## Why it exists

Three tickets produce content an LLM drafts that could eventually reach a student:

- **#69** (misconception rule drafts, done) — `_validate_draft()` is explicitly structural
  only ("is the JSON shape right"), not a safety gate, per its own out-of-scope note.
- **#70** (hint-variant pool, not started) — needs the same kind of human approval gate
  #69 already has, but nothing yet defines what that human is checking for.
- **#72** (live level-2 hint phrasing, not started) — its own AC already lists "length cap,
  no answer leakage, Dutch, age-appropriate" as validation requirements, but with no
  concrete definition of what those mean or how to check them at runtime.

This doc is the missing piece: one written bar, consolidated from decisions already made
elsewhere in this project (not invented here), concrete enough that a human reviewer and
an automated validator can both use it.

## The four criteria

1. **No answer-revealing content** — doesn't give away the correct answer or make the next
   step trivially obvious. Nudges the student toward noticing their mistake; doesn't solve
   it for them.
2. **Age-appropriate Dutch phrasing** — Dutch only (matches the API contract's "Language:
   Dutch only for MVP"), phrased for a groep 7-8 (10-12yo) audience. Calibration reference:
   ticket #35's confirmed generic-hint wording uses `"som"` (kid-friendly "a math problem"),
   not the more formal/textbook `"berekening"` — the same register applies here.
3. **Factual/mathematical correctness** — a misconception rule's `check`/
   `wrong_result_template` genuinely represents a real error pattern; a hint's mathematical
   claims are actually true.
4. **Encouraging tone** — leads with encouragement, not a flat negative. Calibration
   reference: #35's confirmed opener `"Bijna goed!"` ("Almost right!") — consistent with
   that existing decision, not a competing new tone standard.

## How it applies

### Offline pools (#69, #70)

A human checks each of the four items before approving. `approve_and_seed_rule()` (#69,
already built) and #70's not-yet-built equivalent approval step are the enforcement
points — this checklist is what the human checks against before calling them. Nothing an
LLM drafts here reaches `misconception_rules` or a hint pool without that explicit human
approval step (already true by design for #69; must remain true for #70 too).

### Live escalation (#72)

Nobody manually reviews a live-generated hint before a student sees it — the validation
has to be automated. Translating each criterion into what's actually checkable at
runtime, honestly, rather than overclaiming coverage:

| Criterion | Automatable at runtime? | How |
|---|---|---|
| No answer-revealing | Yes | Length cap on the output, plus a check that the output doesn't contain the problem's `correct_answer` as a substring |
| Dutch phrasing | Yes | A language check on the output |
| Mathematical correctness | **No — not fully** | A live LLM call can't be proven mathematically correct by a cheap runtime check. This is why #72's AC already includes "falls back to a static hint if validation fails" — that fallback covers the case where correctness can't be confirmed, not just outright content rejection |
| Encouraging tone | Partially | A heuristic check (e.g. a banned flat-negative-opener list) — acknowledged as imperfect, not a guarantee |

This table is what #72 builds its automated validation rules against, instead of starting
from "length cap, no answer leakage, Dutch, age-appropriate" with no further definition.

## What this explicitly is not

- Not a UI or enforcement mechanism itself — it's the written standard that #69/#70's human
  approval steps and #72's automated validation are built against.
- Not a change to #69's `_validate_draft()` — that stays correctly scoped to structural
  JSON-shape validation only; safety/content review is a separate step, covered here.
- Not new criteria invented from scratch — all four are consolidated from #35's confirmed
  wording decision and #72's own existing AC.
