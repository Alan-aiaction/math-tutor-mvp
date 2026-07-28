# API Contract — Draft (Task #11)
> Status: DRAFT — for discussion, not yet agreed. Bring to team call before treating any of this as final.
> Covers the "Domain Models / Schemas (Pydantic)" box in the architecture diagram.

## Purpose

Before frontend, backend, and content work proceed independently, all three of us need to
agree on the exact shape of the data passed between frontend ↔ backend ↔ database. This doc
is a starting proposal — not a decision — to make that conversation concrete instead of
starting from a blank page.

Once agreed, this becomes `backend/models.py` (Pydantic classes) and directly maps to the
Supabase schema (task #6).

---

## 1. Problem

A single math question presented to the student.

```python
class Problem(BaseModel):
    id: int
    topic: str              # e.g. "fractions", "percentages"
    difficulty: int         # 1-5, TBD scale — confirm with team
    question_text: str
    correct_answer: str
```

**Open questions:**
- Is `difficulty` a number (1-5) or a label ("easy"/"medium"/"hard")?
- Does `correct_answer` need to support multiple equivalent forms (e.g. 1/2 = 0.5 = 50%)?

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
    matching_rule: str       # pattern used by the rule-matching engine
    escalation_hint_id: str | None
```

**Open questions:**
- What does `matching_rule` actually look like technically (regex? structured comparison? something else)? This affects how Jeff builds the rule-matching engine (task #30).

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

1. Review as a team — adjust field names/types together, don't treat this as final
2. Resolve the open questions listed under each model
3. Once agreed, commit as `backend/models.py`
4. Cross-check against the Supabase schema (task #6) so table columns match these fields exactly
