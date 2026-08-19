"""Integration test for the KPI data layer: hits the real, live Supabase project.

Requires real SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY credentials (from backend/.env)
to pass - nothing here is mocked, matching test_attempts_integration.py's convention.

Creates its own throwaway parent, child, problem, and attempts (via the real
create_attempt(), not raw inserts, so this also exercises the previous_wrong_count/
created_at persistence path end to end), and cleans everything up in teardown.
"""
import uuid

import pytest
from dotenv import load_dotenv

from attempts import create_attempt
from db import get_client
from kpis import (
    get_accuracy_trend,
    get_average_retries,
    get_practice_frequency,
    get_total_attempts,
    get_weak_spots_by_topic,
)

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
                "question_text": "1/4 + 1/3 (test fixture, kpis integration test)",
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
    email = f"test-kpis-integration-{uuid.uuid4()}@example.com"
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


def test_kpis_computed_from_real_persisted_attempts(throwaway_problem, throwaway_child):
    client = get_client()
    child_id = throwaway_child["id"]
    problem_id = throwaway_problem["id"]

    attempt_ids = []
    try:
        # One correct step, no retries.
        a1 = create_attempt(
            problem_id=problem_id,
            child_id=child_id,
            status="completed",
            steps=[{"recognized_latex": "7/12", "is_correct": True, "previous_wrong_count": 0}],
        )
        attempt_ids.append(a1.id)

        # One wrong step, after 2 prior wrong tries.
        a2 = create_attempt(
            problem_id=problem_id,
            child_id=child_id,
            status="completed",
            steps=[{"recognized_latex": "5/7", "is_correct": False, "previous_wrong_count": 2}],
        )
        attempt_ids.append(a2.id)

        trend = get_accuracy_trend(child_id)
        assert len(trend) == 1  # both attempts created today
        assert trend[0]["accuracy"] == 0.5  # 1 correct out of 2 steps total

        frequency = get_practice_frequency(child_id)
        assert frequency == 1  # both attempts on the same day

        avg_retries = get_average_retries(child_id)
        assert avg_retries == 1.0  # (0 + 2) / 2

        weak_spots = get_weak_spots_by_topic(child_id)
        assert weak_spots == [{"topic": "fractions", "accuracy": 0.5}]

        assert get_total_attempts(child_id) == 2
    finally:
        for attempt_id in attempt_ids:
            client.table("attempt_steps").delete().eq("attempt_id", attempt_id).execute()
            client.table("attempts").delete().eq("id", attempt_id).execute()


def test_kpis_empty_state_for_a_child_with_no_attempts(throwaway_child):
    child_id = throwaway_child["id"]
    assert get_accuracy_trend(child_id) == []
    assert get_practice_frequency(child_id) == 0
    assert get_average_retries(child_id) == 0.0
    assert get_weak_spots_by_topic(child_id) == []
    assert get_total_attempts(child_id) == 0
