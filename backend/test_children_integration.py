"""Integration test for children.py (3rd MVP) against the real Supabase project.

Requires real SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY (from backend/.env). Creates a real
throwaway parent (via supabase-py's admin API - children.parent_id has a real FK to
auth.users) and real throwaway children rows, exercising create/list/verify for real,
cleaned up after.
"""
import uuid

import pytest
from dotenv import load_dotenv

from attempts import create_attempt
from children import ChildError, create_child, delete_child, get_child, list_children, verify_child_login
from db import get_client

load_dotenv()


@pytest.fixture
def throwaway_parent():
    client = get_client()
    email = f"test-children-integration-{uuid.uuid4()}@example.com"
    user = client.auth.admin.create_user(
        {"email": email, "password": "throwaway-test-password", "email_confirm": True}
    ).user
    yield user.id
    client.table("children").delete().eq("parent_id", user.id).execute()
    client.auth.admin.delete_user(user.id)


@pytest.fixture
def throwaway_problem():
    client = get_client()
    row = (
        client.table("problems")
        .insert(
            {
                "topic": "fractions",
                "difficulty": 1,
                "question_text": "1/4 + 1/3 (test fixture, delete-child integration test)",
                "correct_answer": "7/12",
            }
        )
        .execute()
        .data[0]
    )
    yield row
    client.table("problems").delete().eq("id", row["id"]).execute()


def test_create_list_and_login_a_real_child(throwaway_parent):
    child = create_child(throwaway_parent, "Sam", "sesame")
    assert child.nickname == "Sam"
    assert child.parent_id == throwaway_parent

    listed = list_children(throwaway_parent)
    assert len(listed) == 1
    assert listed[0].id == child.id

    fetched = get_child(throwaway_parent, child.id)
    assert fetched is not None
    assert fetched.nickname == "Sam"

    assert verify_child_login(throwaway_parent, child.id, "sesame") is True
    assert verify_child_login(throwaway_parent, child.id, "wrong-password") is False


def test_duplicate_nickname_for_the_same_parent_raises_child_error(throwaway_parent):
    create_child(throwaway_parent, "Sam", "sesame")
    with pytest.raises(ChildError):
        create_child(throwaway_parent, "Sam", "different-password")


def test_a_childs_id_is_not_visible_to_a_different_parent(throwaway_parent):
    child = create_child(throwaway_parent, "Sam", "sesame")
    real_but_wrong_parent = "00000000-0000-0000-0000-000000000000"
    assert get_child(real_but_wrong_parent, child.id) is None
    assert verify_child_login(real_but_wrong_parent, child.id, "sesame") is False


def test_delete_child_removes_the_child_and_all_their_attempt_history(throwaway_parent, throwaway_problem):
    client = get_client()
    child = create_child(throwaway_parent, "Sam", "sesame")
    attempt = create_attempt(
        problem_id=throwaway_problem["id"],
        child_id=child.id,
        status="completed",
        steps=[{"recognized_latex": "7/12", "is_correct": True}],
    )

    result = delete_child(throwaway_parent, child.id)

    assert result is True
    assert get_child(throwaway_parent, child.id) is None
    assert client.table("attempts").select("id").eq("id", attempt.id).execute().data == []
    assert client.table("attempt_steps").select("id").eq("attempt_id", attempt.id).execute().data == []


def test_delete_child_not_owned_by_this_parent_returns_false_and_leaves_child_intact(throwaway_parent):
    child = create_child(throwaway_parent, "Sam", "sesame")
    real_but_wrong_parent = "00000000-0000-0000-0000-000000000000"

    result = delete_child(real_but_wrong_parent, child.id)

    assert result is False
    assert get_child(throwaway_parent, child.id) is not None
