"""Integration test for task #14: hits the real, live Supabase project.

Requires real SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY credentials (from backend/.env)
to pass - nothing here is mocked, matching test_db_integration.py's convention.

Creates its own throwaway problem row rather than relying on #8's specific seeded
rows/ids, so this stays correct even if that content changes later. Deletes it in
teardown - leaves the live DB clean.
"""
import pytest
from dotenv import load_dotenv

from db import get_client
from problems import ProblemNotFoundError, get_problem

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
                "question_text": "1/4 + 1/3 (test fixture, task #14 integration test)",
                "correct_answer": "7/12",
            }
        )
        .execute()
        .data[0]
    )
    yield row
    client.table("problems").delete().eq("id", row["id"]).execute()


def test_get_problem_returns_real_seeded_row(throwaway_problem):
    result = get_problem(throwaway_problem["id"])
    assert result.id == throwaway_problem["id"]
    assert result.correct_answer == "7/12"


def test_get_problem_raises_not_found_for_real_nonexistent_id():
    with pytest.raises(ProblemNotFoundError):
        get_problem(999999999)
