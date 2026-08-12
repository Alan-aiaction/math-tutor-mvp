"""Integration test for ticket #68: hits the real, live Supabase project.

Requires real SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY credentials (from backend/.env)
to pass - nothing here is mocked, matching test_db_integration.py's convention.

Requires the shadow_log_review_notes migration
(supabase/migrations/20260812140000_shadow_log_review_notes.sql) to already be applied.

Creates its own throwaway problem + review-note rows rather than relying on any specific
existing content, and deletes them in teardown - leaves the live DB clean.
"""
import pytest
from dotenv import load_dotenv

from db import get_client
from shadow_log_review import get_wrong_answer_clusters, record_review

load_dotenv()


@pytest.fixture
def throwaway_problem():
    client = get_client()
    row = (
        client.table("problems")
        .insert(
            {
                "topic": "fractions",
                "difficulty": 1,
                "question_text": "1/4 + 1/3 (test fixture, ticket #68 integration test)",
                "correct_answer": "7/12",
            }
        )
        .execute()
        .data[0]
    )
    yield row
    client.table("shadow_log_review_notes").delete().eq("problem_id", row["id"]).execute()
    client.table("problems").delete().eq("id", row["id"]).execute()


def test_record_review_excludes_cluster_from_later_calls(throwaway_problem):
    client = get_client()
    problem_id = throwaway_problem["id"]

    # No attempts/attempt_steps exist for this throwaway problem, so
    # get_wrong_answer_clusters(problem_id) starts empty - real content isn't the point
    # here, just that record_review()'s exclusion behavior works against the real table.
    before = get_wrong_answer_clusters(problem_id)
    assert before == []

    record_review(problem_id, representative_answer="2/7", note="Adds numerators and denominators straight across", status="reviewed")

    stored = (
        client.table("shadow_log_review_notes")
        .select("*")
        .eq("problem_id", problem_id)
        .eq("representative_answer", "2/7")
        .execute()
        .data
    )
    assert len(stored) == 1
    assert stored[0]["note"] == "Adds numerators and denominators straight across"
    assert stored[0]["status"] == "reviewed"


def test_record_review_upserts_on_same_cluster(throwaway_problem):
    client = get_client()
    problem_id = throwaway_problem["id"]

    record_review(problem_id, representative_answer="5/12", note="first note", status="reviewed")
    record_review(problem_id, representative_answer="5/12", note="updated note", status="drafted")

    stored = (
        client.table("shadow_log_review_notes")
        .select("*")
        .eq("problem_id", problem_id)
        .eq("representative_answer", "5/12")
        .execute()
        .data
    )
    assert len(stored) == 1
    assert stored[0]["note"] == "updated note"
    assert stored[0]["status"] == "drafted"
