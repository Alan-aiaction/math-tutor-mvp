"""Integration test for parents.py against the real Supabase project.

Requires real SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY (from backend/.env). Creates a
real throwaway parent (via supabase-py's admin API - parents.id has a real FK to
auth.users), exercising get_or_create_parent for real, cleaned up after.
"""
import uuid

import pytest
from dotenv import load_dotenv

from children import ChildError, create_child, get_child_by_nickname, verify_child_login
from db import get_client
from parents import DEFAULT_MAX_CHILDREN, get_or_create_parent, get_parent_by_family_code

load_dotenv()


@pytest.fixture
def throwaway_parent():
    client = get_client()
    email = f"test-parents-integration-{uuid.uuid4()}@example.com"
    user = client.auth.admin.create_user(
        {"email": email, "password": "throwaway-test-password", "email_confirm": True}
    ).user
    yield user.id
    client.table("children").delete().eq("parent_id", user.id).execute()
    client.table("parents").delete().eq("id", user.id).execute()
    client.auth.admin.delete_user(user.id)


def test_get_or_create_parent_creates_then_reuses_the_same_row(throwaway_parent):
    first = get_or_create_parent(throwaway_parent)
    assert first.id == throwaway_parent
    assert len(first.family_code) == 6
    assert first.max_children == DEFAULT_MAX_CHILDREN

    second = get_or_create_parent(throwaway_parent)
    assert second.family_code == first.family_code


def test_create_child_enforces_the_real_cap(throwaway_parent):
    parent = get_or_create_parent(throwaway_parent)
    client = get_client()
    client.table("parents").update({"max_children": 2}).eq("id", throwaway_parent).execute()

    create_child(throwaway_parent, "Sam", "sesame")
    create_child(throwaway_parent, "Odin", "sesame")

    with pytest.raises(ChildError):
        create_child(throwaway_parent, "Ian", "sesame")


def test_independent_child_login_lookup_chain_end_to_end(throwaway_parent):
    """Exercises the exact real-DB lookup chain POST /children/login uses: family_code
    -> parent, then (parent, nickname) -> child, then the existing password check -
    without going through the endpoint itself (that's covered at the unit level in
    test_main.py with mocks)."""
    parent = get_or_create_parent(throwaway_parent)
    create_child(throwaway_parent, "Sam", "sesame")

    found_parent = get_parent_by_family_code(parent.family_code)
    assert found_parent is not None
    assert found_parent.id == throwaway_parent

    found_child = get_child_by_nickname(found_parent.id, "Sam")
    assert found_child is not None
    assert found_child.nickname == "Sam"

    assert verify_child_login(found_parent.id, found_child.id, "sesame") is True
    assert verify_child_login(found_parent.id, found_child.id, "wrong-password") is False
    assert get_child_by_nickname(found_parent.id, "NotReal") is None
    assert get_parent_by_family_code("NOTAREALCODE") is None
