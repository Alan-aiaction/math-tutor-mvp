"""Domain models agreed in docs/architecture/api_contract_draft_20260728.md (task #11).

Kept in sync with that doc - see it for field-level open questions and reasoning, and
docs/tracking/decision-log.md for the decisions behind solving_tip, matching_rule, etc.
"""

from pydantic import BaseModel


class Problem(BaseModel):
    id: int
    topic: str  # e.g. "fractions", "percentages"
    difficulty: int  # 1-5 - proposed 2026-08-03, pending team confirmation
    question_text: str
    correct_answer: str
    solving_tip: str | None  # per-problem worked-strategy hint, shown regardless of the
    # student's answer. Distinct from Hint (which is reactive, keyed to a misconception).


class Step(BaseModel):
    id: int
    attempt_id: int
    recognized_latex: str  # output from MyScript recognition
    is_correct: bool


class Attempt(BaseModel):
    id: int
    problem_id: int
    student_id: str  # the access code from task #50
    steps: list[Step]
    status: str  # e.g. "in_progress", "completed" - fixed value list still open


class EvaluationResult(BaseModel):
    valid: bool
    misconception_id: str | None
    hint_text: str | None


class Misconception(BaseModel):
    id: str
    topic: str
    description: str
    matching_rule: dict  # structured comparison, stored as jsonb - exact sub-schema is #29's job
    escalation_hint_id: str | None  # not an enforced FK in storage - see decision log


class Hint(BaseModel):
    id: str
    misconception_id: str
    text: str
    level: int  # e.g. 1 = first hint, 2 = escalated/more direct
