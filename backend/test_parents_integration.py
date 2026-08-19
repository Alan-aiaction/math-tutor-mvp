"""Integration test for parents.py against the real Supabase project.

Requires real SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY (from backend/.env). Creates a
real throwaway parent (via supabase-py's admin API - parents.id has a real FK to
auth.users), exercising get_or_create_parent for real, cleaned up after.
"""
import uuid

import pytest
from dotenv import load_dotenv

from children import ChildError, create_child
from db import get_client
from parents import DEFAULT_MAX_CHILDREN, get_or_create_parent

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
