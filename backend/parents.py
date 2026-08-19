"""Parent profile management (independent child login + child cap groundwork).

A parent's own `auth.users` row is created by Supabase Auth at sign-up; this module
owns a small companion row in `parents` for the two things Supabase Auth has no place
for: the family code a child uses to log in independently (see children.py's future
login flow), and the per-parent cap on how many children they can create. The row is
created lazily on first use, not at sign-up time, so a parent who signed up before this
feature shipped isn't left in a broken state.
"""
import secrets

from db import get_client
from models import Parent

DEFAULT_MAX_CHILDREN = 3

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
