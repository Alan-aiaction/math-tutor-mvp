"""Integration test for task #15: hits the real, live Supabase project.

Requires real SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY credentials (from backend/.env)
to pass - nothing here is mocked, matching test_db_integration.py's convention.

The `problems` table is empty (#8 hasn't seeded real content yet), so this test creates
its own throwaway problem row to get a valid problem_id, and deletes everything it
created (steps, attempt, problem) during teardown - leaves the live DB clean, not
accumulating test junk in a table meant to hold real student data.

3rd MVP: attempts.child_id has a real FK to children, which has a real FK to
auth.users - so this test also needs a real throwaway parent (via supabase-py's admin
API) and a real throwaway child underneath it, both cleaned up in teardown.
"""
import uuid

import pytest
from dotenv import load_dotenv

from attempts import create_attempt
from db import get_client

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
                "question_text": "1/4 + 1/3 (test fixture, task #15 integration test)",
                "correct_answer": "7/12",
            }
        )
        .execute()
        .data[0]
    )
    yield row
    client.table("problems").delete().eq("id", row["id"]).execute()


@pytest.fixture
def throwaway_child():
    client = get_client()
    email = f"test-attempts-integration-{uuid.uuid4()}@example.com"
    user = client.auth.admin.create_user(
        {"email": email, "password": "throwaway-test-password", "email_confirm": True}
    ).user
    child_row = (
        client.table("children")
        .insert({"parent_id": user.id, "nickname": "TestChild", "password_hash": "unused-in-this-test"})
        .execute()
        .data[0]
    )
    yield child_row
    client.table("children").delete().eq("id", child_row["id"]).execute()
    client.auth.admin.delete_user(user.id)


def test_create_attempt_persists_and_is_queryable(throwaway_problem, throwaway_child):
    client = get_client()

    result = create_attempt(
        problem_id=throwaway_problem["id"],
        child_id=throwaway_child["id"],
        status="in_progress",
        steps=[{"recognized_latex": "7/12", "is_correct": True, "previous_wrong_count": 2}],
    )

    try:
        assert result.id is not None
        assert result.created_at is not None
        assert len(result.steps) == 1
        assert result.steps[0].previous_wrong_count == 2

        queried_attempt = (
            client.table("attempts").select("*").eq("id", result.id).execute().data
        )
        assert len(queried_attempt) == 1
        assert queried_attempt[0]["problem_id"] == throwaway_problem["id"]
        assert queried_attempt[0]["created_at"] is not None

        queried_steps = (
            client.table("attempt_steps").select("*").eq("attempt_id", result.id).execute().data
        )
        assert len(queried_steps) == 1
        assert queried_steps[0]["recognized_latex"] == "7/12"
        assert queried_steps[0]["previous_wrong_count"] == 2
    finally:
        client.table("attempt_steps").delete().eq("attempt_id", result.id).execute()
        client.table("attempts").delete().eq("id", result.id).execute()
