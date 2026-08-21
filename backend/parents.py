"""Parent profile management (independent child login + child cap groundwork).

A parent's own `auth.users` row is created by Supabase Auth at sign-up; this module
owns a small companion row in `parents` for the two things Supabase Auth has no place
for: the family code a child uses to log in independently (see children.py's future
login flow), and the per-parent cap on how many children they can create. The row is
created lazily on first use, not at sign-up time, so a parent who signed up before this
feature shipped isn't left in a broken state.
"""
import os
import secrets

from db import get_client
from models import Parent

DEFAULT_MAX_CHILDREN = 3

# Lifetime cap, not a monthly/rolling one - this is pre-billing, invite-only testing
# (mainly the demo accounts), so there's no subscription period to reset against yet.
# A config value, not a code change, once real usage data suggests a different number.
# Read live (not cached at import time) so a test's monkeypatch - or, in production, an
# actual env var change on redeploy - takes effect without needing a process restart
# mid-test-session.
DEFAULT_LLM_TOKEN_LIMIT_PER_ACCOUNT = 20000


def _llm_token_limit_per_account() -> int:
    return int(os.environ.get("LLM_TOKEN_LIMIT_PER_ACCOUNT", DEFAULT_LLM_TOKEN_LIMIT_PER_ACCOUNT))

# No 0/O/1/I/L - a parent reads or writes this code out for a child by hand or aloud,
# and those are the classic handwriting/read-aloud confusions.
_CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
_CODE_LENGTH = 6


def _generate_family_code() -> str:
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(_CODE_LENGTH))


def _to_parent(row: dict) -> Parent:
    return Parent(
        id=row["id"],
        family_code=row["family_code"],
        max_children=row["max_children"],
        # .get(..., 0), not row[...]: existing rows (and every pre-existing test mock)
        # predate this column - default to 0 rather than requiring every caller/fixture
        # to be updated for a field that's 0 for everyone until a real LLM_API_KEY ever
        # gets used anyway.
        llm_tokens_used=row.get("llm_tokens_used", 0),
        created_at=row["created_at"],
    )


def get_or_create_parent(parent_id: str) -> Parent:
    """Fetch this parent's profile row, creating it with a fresh family code and the
    default child cap if it doesn't exist yet."""
    client = get_client()
    rows = client.table("parents").select("*").eq("id", parent_id).execute().data
    if rows:
        return _to_parent(rows[0])

    last_exc: Exception | None = None
    for _ in range(5):
        try:
            row = (
                client.table("parents")
                .insert({"id": parent_id, "family_code": _generate_family_code(), "max_children": DEFAULT_MAX_CHILDREN})
                .execute()
                .data[0]
            )
            return _to_parent(row)
        except Exception as exc:  # family_code collision (astronomically rare) - retry with a new code
            last_exc = exc
    raise RuntimeError(f"Could not create parent profile after 5 attempts: {last_exc}")


def get_parent_by_family_code(family_code: str) -> Parent | None:
    """Look up a parent by their family code - the entry point for independent child
    login (PR 2/3), where there's no parent session yet to key off instead."""
    client = get_client()
    rows = client.table("parents").select("*").eq("family_code", family_code).execute().data
    if not rows:
        return None
    return _to_parent(rows[0])


def has_reached_llm_token_limit(parent_id: str) -> bool:
    """True once this account's lifetime LLM token usage has reached
    LLM_TOKEN_LIMIT_PER_ACCOUNT - checked by hint_escalation_llm.py before making a
    live LLM call, so an account that's used up its budget falls back to the static
    generic hint instead."""
    parent = get_or_create_parent(parent_id)
    return parent.llm_tokens_used >= _llm_token_limit_per_account()


def record_llm_tokens_used(parent_id: str, tokens_used: int) -> None:
    """Add tokens_used to this account's running total - called once, after a
    successful live LLM call, with the real token count that call actually cost.

    A plain read-modify-write, not an atomic increment: at this account count and
    request volume a same-instant race is vanishingly unlikely, and a dedicated
    Postgres function is more machinery than that risk justifies right now."""
    client = get_client()
    parent = get_or_create_parent(parent_id)
    client.table("parents").update({"llm_tokens_used": parent.llm_tokens_used + tokens_used}).eq(
        "id", parent_id
    ).execute()
