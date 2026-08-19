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
    previous_wrong_count: int = 0  # KPI data layer: how many times this step already
    # came back wrong before this save - see main.py's StepCreate for the full note


class Attempt(BaseModel):
    id: int
    problem_id: int
    child_id: int  # 3rd MVP: replaces the old free-text student_id access code (#50) -
    # a real FK to a parent-owned child account, see children.py
    steps: list[Step]
    status: str  # e.g. "in_progress", "completed" - fixed value list still open
    created_at: str  # KPI data layer: powers accuracy-trend/practice-frequency queries


class Child(BaseModel):
    id: int
    parent_id: str  # a Supabase Auth user id (uuid) - the owning parent
    nickname: str
    created_at: str  # never includes password_hash - that never leaves children.py


class Parent(BaseModel):
    id: str  # a Supabase Auth user id (uuid) - same id as auth.users, not a new one
    family_code: str  # short, unambiguous code a parent hands to their child for
    # independent login (see parents.py) - not a secret on its own, always paired
    # with the child's own nickname + password
    max_children: int  # per-parent cap; fixed default until a real billing system
    # exists to vary it per plan (deferred to 4th MVP)
    created_at: str


class EvaluationResult(BaseModel):
    valid: bool
    misconception_id: str | None
    hint_text: str | None
    hint_level: int | None = None  # ticket #71: 1 = first hint, 2 = escalated -
    # None (not 0) when valid=True, matching hint_text/misconception_id's own
    # None-when-correct convention. Default preserves every pre-#71 caller.


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
