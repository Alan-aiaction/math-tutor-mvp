"""LLM-assisted misconception rule drafting (ticket #69, 2nd MVP).

Turns a human-reviewed shadow-log pattern (ticket #68's record_review() note) into a
structured misconception_rules draft, using the LLM provider-abstraction layer (ticket
#67) - never a vendor SDK directly, never auto-seeded. A human must explicitly call
approve_and_seed_rule() before anything reaches misconception_rules; draft_rule_from_note()
only ever writes to the review-tracking table, same offline-authoring, human-in-the-loop
design already committed to in docs/architecture/proposal_misconception_rule_format.md
(Fig. 2's left loop).

Rule shape (Fig. 1 of that doc): {id, topic, description, matching_rule: {operation,
error_transform, check: {type, wrong_result_template}}} - matches backend/models.py's
Misconception model exactly, so an approved draft can be seeded as-is.
"""
import json

from db import get_client
from llm import generate_text
from problems import get_problem

# The proposal doc's own two worked examples, reused as few-shot prompt context instead of
# inventing new ones.
_FEW_SHOT_EXAMPLES = """\
Example 1:
operation: fraction_addition
error_transform: add_numerators_and_denominators
check.type: symbolic_equivalence
check.wrong_result_template: (a+c)/(b+d)
(A student adding 1/3 + 1/4 straight across to get 2/7, instead of finding a common denominator.)

Example 2:
operation: fraction_subtraction
error_transform: subtract_numerators_and_denominators
check.type: symbolic_equivalence
check.wrong_result_template: (a-c)/(b-d)
"""

_REQUIRED_TOP_LEVEL_KEYS = {"id", "topic", "description", "matching_rule"}
_REQUIRED_MATCHING_RULE_KEYS = {"operation", "error_transform", "check"}
_REQUIRED_CHECK_KEYS = {"type", "wrong_result_template"}


class RuleDraftError(Exception):
    """Raised when a cluster can't be drafted (no review note, malformed LLM output)."""


def _build_prompt(question_text: str, correct_answer: str, representative_answer: str, note: str) -> str:
    return f"""You are drafting a structured misconception rule for a Dutch groep 7-8 math tutor.

Problem: {question_text}
Correct answer: {correct_answer}
A student's wrong answer: {representative_answer}
Human's description of the mistake: {note}

{_FEW_SHOT_EXAMPLES}

Respond with ONLY valid JSON (no prose, no markdown fences) matching this exact shape:
{{
  "id": "short_snake_case_slug",
  "topic": "topic name, e.g. fractions",
  "description": "genuinely descriptive explanation of the misconception",
  "matching_rule": {{
    "operation": "operation category",
    "error_transform": "name of the specific known mistake",
    "check": {{
      "type": "symbolic_equivalence",
      "wrong_result_template": "template expression using a, b, c, d for operands"
    }}
  }}
}}"""


def _validate_draft(draft: dict) -> None:
    if not _REQUIRED_TOP_LEVEL_KEYS.issubset(draft.keys()):
        raise RuleDraftError(f"Drafted rule missing required keys: {_REQUIRED_TOP_LEVEL_KEYS - draft.keys()}")
    matching_rule = draft["matching_rule"]
    if not isinstance(matching_rule, dict) or not _REQUIRED_MATCHING_RULE_KEYS.issubset(matching_rule.keys()):
        raise RuleDraftError("Drafted rule's matching_rule is missing required keys (operation, error_transform, check)")
    check = matching_rule["check"]
    if not isinstance(check, dict) or not _REQUIRED_CHECK_KEYS.issubset(check.keys()):
        raise RuleDraftError("Drafted rule's matching_rule.check is missing required keys (type, wrong_result_template)")


def draft_rule_from_note(problem_id: int, representative_answer: str) -> dict:
    """Draft a structured misconception rule from a reviewed shadow-log cluster.

    Requires a review note to already exist (ticket #68's record_review()). Stores the
    validated draft back onto that same row and advances status to "drafted" - does NOT
    seed it into misconception_rules. Raises RuleDraftError on a missing note or malformed
    LLM output.
    """
    client = get_client()
    rows = (
        client.table("shadow_log_review_notes")
        .select("*")
        .eq("problem_id", problem_id)
        .eq("representative_answer", representative_answer)
        .execute()
        .data
    )
    if not rows:
        raise RuleDraftError(f"No review note found for problem {problem_id}, answer {representative_answer!r}")
    note = rows[0]["note"]

    problem = get_problem(problem_id)
    prompt = _build_prompt(problem.question_text, problem.correct_answer, representative_answer, note)

    response_text = generate_text(prompt)
    try:
        draft = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise RuleDraftError(f"LLM response was not valid JSON: {exc}") from exc

    _validate_draft(draft)

    client.table("shadow_log_review_notes").update(
        {"drafted_rule": draft, "status": "drafted"}
    ).eq("problem_id", problem_id).eq("representative_answer", representative_answer).execute()

    return draft


def approve_and_seed_rule(problem_id: int, representative_answer: str) -> None:
    """Seed an already-drafted, human-approved rule into misconception_rules.

    Requires draft_rule_from_note() to have already stored a draft for this cluster.
    Advances shadow_log_review_notes.status to "seeded".
    """
    client = get_client()
    rows = (
        client.table("shadow_log_review_notes")
        .select("*")
        .eq("problem_id", problem_id)
        .eq("representative_answer", representative_answer)
        .execute()
        .data
    )
    if not rows or not rows[0].get("drafted_rule"):
        raise RuleDraftError(f"No drafted rule found for problem {problem_id}, answer {representative_answer!r}")
    draft = rows[0]["drafted_rule"]

    client.table("misconception_rules").insert(
        {
            "id": draft["id"],
            "topic": draft["topic"],
            "description": draft["description"],
            "matching_rule": draft["matching_rule"],
        }
    ).execute()

    client.table("shadow_log_review_notes").update({"status": "seeded"}).eq(
        "problem_id", problem_id
    ).eq("representative_answer", representative_answer).execute()
