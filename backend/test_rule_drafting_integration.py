"""Integration test for ticket #69: hits the real, live Supabase project.

Requires real SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY credentials (from backend/.env)
to pass - nothing here is mocked except the LLM call itself (draft_rule_from_note()'s
generate_text() call is mocked so this test doesn't hit a real paid API - matching this
repo's convention of never calling a real paid third-party API in the test suite).

Creates its own throwaway problem + review-note + drafted rule, deletes them in
teardown - leaves the live DB clean.
"""
import json
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from db import get_client
from rule_drafting import approve_and_seed_rule, draft_rule_from_note
from shadow_log_review import record_review

load_dotenv()

DRAFTED_RULE = {
    "id": "frac_add_denominators_test_fixture",
    "topic": "fractions",
    "description": "Adds numerators and denominators straight across (ticket #69 integration test fixture)",
    "matching_rule": {
        "operation": "fraction_addition",
        "error_transform": "add_numerators_and_denominators",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "(a+c)/(b+d)"},
    },
}


@pytest.fixture
def throwaway_problem_with_review_note():
    client = get_client()
    row = (
        client.table("problems")
        .insert(
            {
                "topic": "fractions",
                "difficulty": 1,
                "question_text": "1/3 + 1/4 (test fixture, ticket #69 integration test)",
                "correct_answer": "7/12",
            }
        )
        .execute()
        .data[0]
    )
    record_review(row["id"], representative_answer="2/7", note="Adds numerators and denominators straight across")
    yield row
    client.table("misconception_rules").delete().eq("id", DRAFTED_RULE["id"]).execute()
    client.table("shadow_log_review_notes").delete().eq("problem_id", row["id"]).execute()
    client.table("problems").delete().eq("id", row["id"]).execute()


def test_draft_then_approve_seeds_a_real_misconception_rule(throwaway_problem_with_review_note):
    client = get_client()
    problem_id = throwaway_problem_with_review_note["id"]

    with patch("rule_drafting.generate_text", return_value=json.dumps(DRAFTED_RULE)):
        draft = draft_rule_from_note(problem_id, representative_answer="2/7")

    assert draft == DRAFTED_RULE

    note_row = (
        client.table("shadow_log_review_notes")
        .select("*")
        .eq("problem_id", problem_id)
        .eq("representative_answer", "2/7")
        .execute()
        .data[0]
    )
    assert note_row["status"] == "drafted"
    assert note_row["drafted_rule"] == DRAFTED_RULE

    approve_and_seed_rule(problem_id, representative_answer="2/7")

    seeded = (
        client.table("misconception_rules")
        .select("*")
        .eq("id", DRAFTED_RULE["id"])
        .execute()
        .data
    )
    assert len(seeded) == 1
    assert seeded[0]["topic"] == "fractions"
    assert seeded[0]["matching_rule"] == DRAFTED_RULE["matching_rule"]

    note_row_after = (
        client.table("shadow_log_review_notes")
        .select("status")
        .eq("problem_id", problem_id)
        .eq("representative_answer", "2/7")
        .execute()
        .data[0]
    )
    assert note_row_after["status"] == "seeded"
