"""Child account management (3rd MVP).

A child is deliberately NOT a second independent Supabase Auth identity - only the
parent is (see auth.py). A child is a row in `children`, owned by a parent (parent_id),
gated by a bcrypt-hashed password this module checks directly - not a cryptographic
session of its own. Every function here is parent_id-scoped: a parent can only ever see,
create, or verify children that belong to them. That ownership check happens on every
call, not just once at "login" time, matching the design decision recorded in
decision-log.md (real Dutch EdTech products for this age range - Squla, Junior Einstein -
use the same shape: parent owns the account, child is a lightweight nested profile).
"""
import bcrypt

from db import get_client
from models import Child


class ChildError(Exception):
    """Raised for a child-account operation that can't complete - a duplicate nickname,
    a child_id that doesn't belong to the requesting parent, or a wrong password."""


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_child(parent_id: str, nickname: str, password: str) -> Child:
    """Create a new child under this parent. Raises ChildError if this parent already
    has a child with the same nickname (the (parent_id, nickname) unique constraint)."""
    client = get_client()
    try:
        row = (
            client.table("children")
            .insert({"parent_id": parent_id, "nickname": nickname, "password_hash": _hash_password(password)})
            .execute()
            .data[0]
        )
    except Exception as exc:
        raise ChildError(f"Could not create child {nickname!r}: {exc}") from exc
    return Child(id=row["id"], parent_id=row["parent_id"], nickname=row["nickname"], created_at=row["created_at"])


def list_children(parent_id: str) -> list[Child]:
    """List every child belonging to this parent, for the child-picker screen."""
    client = get_client()
    rows = client.table("children").select("*").eq("parent_id", parent_id).execute().data
    return [Child(id=r["id"], parent_id=r["parent_id"], nickname=r["nickname"], created_at=r["created_at"]) for r in rows]


def get_child(parent_id: str, child_id: int) -> Child | None:
    """Fetch a child by id, but only if it belongs to this parent - the ownership check
    every other endpoint that touches a specific child_id relies on."""
    client = get_client()
    rows = (
        client.table("children")
        .select("*")
        .eq("id", child_id)
        .eq("parent_id", parent_id)
        .execute()
        .data
    )
    if not rows:
        return None
    row = rows[0]
    return Child(id=row["id"], parent_id=row["parent_id"], nickname=row["nickname"], created_at=row["created_at"])


def verify_child_login(parent_id: str, child_id: int, password: str) -> bool:
    """True if child_id belongs to this parent AND the password matches. False (not an
    exception) on either a wrong password or a child_id that isn't this parent's - the
    caller shouldn't be able to distinguish "wrong password" from "not your child" from
    the response, same principle as not leaking whether a username exists on a login
    form."""
    client = get_client()
    rows = (
        client.table("children")
        .select("password_hash")
        .eq("id", child_id)
        .eq("parent_id", parent_id)
        .execute()
        .data
    )
    if not rows:
        return False
    return _verify_password(password, rows[0]["password_hash"])
