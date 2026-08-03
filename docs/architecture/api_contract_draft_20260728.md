# API Contract (Task #11)
> Status: AGREED — approved by the team 2026-08-02, as written below. The open questions
> listed under each model are non-blocking follow-ups, not blockers — schema (#6) and
> `backend/models.py` (#12) work can proceed against the shapes below as they stand.
> Covers the "Domain Models / Schemas (Pydantic)" box in the architecture diagram.

## Purpose

This is the agreed shape of the data passed between frontend ↔ backend ↔ database, so
frontend, backend, and content work can proceed independently without guessing at each
other's assumptions.

This becomes `backend/models.py` (Pydantic classes) and directly maps to the Supabase
schema (task #6).

---

## 1. Problem

A single math question presented to the student.

```python
class Problem(BaseModel):
    id: int
    topic: str              # e.g. "fractions", "percentages"
    difficulty: int         # 1-5 — proposed 2026-08-03, pending team confirmation
    question_text: str
    correct_answer: str
    solving_tip: str | None  # added 2026-08-03 — per-problem worked-strategy hint, shown
                             # regardless of the student's answer. Distinct from Hint (which
                             # is reactive, keyed to a misconception). Source: groep8 CSV's
                             # "Tip to Solve" column. See docs/tracking/decision-log.md.
```

**Open questions:**
- ~~Is `difficulty` a number (1-5) or a label ("easy"/"medium"/"hard")?~~ Proposed
  2026-08-03: numeric 1-5, plain `integer` column — see
  `docs/tracking/decision-log.md`. Sent to the team, pending confirmation; schema (#6)
  proceeds on this basis in the meantime.
- Does `correct_answer` need to support multiple equivalent forms (e.g. 1/2 = 0.5 = 50%)?
  Already effectively handled at the parser level by #23's canonical-form normalizer, not a
  contract/schema concern.
- Future idea, not a ticket: once the seed problem bank grows past the pilot's ~20-30
  problems, an AI-assisted authoring tool could draft `solving_tip` values using the groep8
  CSV's 64 rows as few-shot examples, with human (Richard) review before anything is seeded
  — same "approved content" pattern already used for hints/rules. Not needed yet at pilot
  scale.

---

## 2. Step

One step the student wrote as part of an attempt.

```python
class Step(BaseModel):
    id: int
    attempt_id: int
    recognized_latex: str   # output from MyScript recognition
    is_correct: bool
```

**Open questions:**
- Do we need a raw confidence score field here too (from MyScript), or handle that only in the Recognition Service internally?

---

## 3. Attempt

A student's full attempt at a problem — one or more steps.

```python
class Attempt(BaseModel):
    id: int
    problem_id: int
    student_id: str         # or access code, pending task #50
    steps: list[Step]
    status: str              # e.g. "in_progress", "completed"
```

**Open questions:**
- What values can `status` take? Needs a fixed list.
- Is `student_id` a real identifier or just the access code from task #50?

---

## 4. EvaluationResult

What comes back after checking a step.

```python
class EvaluationResult(BaseModel):
    valid: bool
    misconception_id: str | None
    hint_text: str | None
```

**Open questions:**
- Does this need an escalation-level field (first-level hint vs. more direct hint after repeated failure)? Not currently captured — flagging since hint escalation is a P0 requirement in the product spec but has no field to carry it yet.

---

## 5. Misconception

A known wrong-answer pattern for a topic.

```python
class Misconception(BaseModel):
    id: str
    topic: str
    description: str
    matching_rule: dict      # structured comparison, stored as jsonb — exact sub-schema
                             # (which operation-types/keys exist) is task #29's job
    escalation_hint_id: str | None  # not an enforced FK in storage — see decision log
```

**Open questions:**
- ~~What does `matching_rule` actually look like technically (regex? structured comparison?
  something else)?~~ Proposed 2026-08-03: structured comparison against the parsed SymPy
  expression tree (not a string/regex), stored as `jsonb` for write-time validation — see
  `docs/tracking/decision-log.md`. Sent to the team, pending confirmation. The *exact*
  operation-type vocabulary inside that JSON structure is still #29's job to define with
  Richard before #9 seeds real rules — this only resolves the outer format (structured vs.
  regex), not the inner schema.

---

## 6. Hint

A pre-authored hint tied to a misconception.

```python
class Hint(BaseModel):
    id: str
    misconception_id: str
    text: str
    level: int                # e.g. 1 = first hint, 2 = escalated/more direct
```

**Open questions:**
- Confirms the escalation mechanic — does `level` cap at 2, or support more steps?
- Language: Dutch only for MVP, per non-goals — confirm no bilingual field needed.

---

## Next steps

1. ~~Review as a team — adjust field names/types together, don't treat this as final~~ Done, approved 2026-08-02
2. Resolve the open questions listed under each model — non-blocking, revisit as they come up
3. Commit as `backend/models.py` (task #12)
4. Cross-check against the Supabase schema (task #6) so table columns match these fields exactly
