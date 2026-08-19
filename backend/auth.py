"""Parent authentication (3rd MVP) + independent child session tokens (PR 2 of 3).

Only the parent is a real Supabase Auth identity - the frontend signs a parent up/in
directly against Supabase (using the anon key, never routed through this backend), then
sends the resulting access token as a Bearer header on every request that needs to act on
behalf of that parent. This module verifies that token server-side and returns the
parent's real user id; it never issues or manages sessions itself.

Child accounts still aren't a second Supabase Auth identity - that call from ticket #76
stands (see children.py's own docstring). What's new here is smaller: once an
independent child proves their family_code + nickname + password (main.py's
POST /children/login), this module issues them a short-lived token of the app's own -
signed with CHILD_SESSION_SECRET, not Supabase's key - so their browser has something to
present on later requests without needing a parent session at all.
"""
import os
import time
from typing import NamedTuple

import jwt

from db import get_client

CHILD_TOKEN_TTL_SECONDS = 24 * 60 * 60  # a practice session is short; requiring
# re-login the next day avoids building refresh-token machinery for this


class AuthError(Exception):
    """Raised when a request's Authorization header is missing, malformed, or the token
    it carries isn't a valid, current Supabase session - callers map this to 401."""


class ChildTokenPayload(NamedTuple):
    child_id: int
    parent_id: str


def get_current_parent_id(authorization_header: str | None) -> str:
    """Extract and verify a parent's Supabase access token, returning their user id.

    authorization_header is the raw HTTP header value, e.g. "Bearer eyJ...". Verification
    happens against Supabase's own auth server (client.auth.get_user), not a locally-held
    JWT secret - one less credential this backend has to manage.
    """
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthError("Missing or malformed Authorization header")

    token = authorization_header.removeprefix("Bearer ").strip()
    if not token:
        raise AuthError("Missing or malformed Authorization header")

    client = get_client()
    try:
        response = client.auth.get_user(token)
    except Exception as exc:
        raise AuthError(f"Invalid or expired token: {exc}") from exc

    if not response or not response.user:
        raise AuthError("Invalid or expired token")

    return response.user.id


def _child_session_secret() -> str:
    secret = os.environ.get("CHILD_SESSION_SECRET")
    if not secret:
        raise AuthError("Child login is not configured (missing CHILD_SESSION_SECRET)")
    return secret


def issue_child_token(child_id: int, parent_id: str) -> str:
    """Signs a short-lived token for an independently-logged-in child - called once,
    right after main.py's POST /children/login verifies their password."""
    payload = {
        "child_id": child_id,
        "parent_id": parent_id,
        "exp": int(time.time()) + CHILD_TOKEN_TTL_SECONDS,
    }
    return jwt.encode(payload, _child_session_secret(), algorithm="HS256")


def get_current_child(authorization_header: str | None) -> ChildTokenPayload:
    """Verifies a child's own session token (not a parent's Supabase token - see
    get_current_parent_id for that). Purely local signature/expiry verification, no
    network round-trip, unlike the parent path."""
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise AuthError("Missing or malformed Authorization header")

    token = authorization_header.removeprefix("Bearer ").strip()
    if not token:
        raise AuthError("Missing or malformed Authorization header")

    try:
        payload = jwt.decode(token, _child_session_secret(), algorithms=["HS256"])
        return ChildTokenPayload(child_id=payload["child_id"], parent_id=payload["parent_id"])
    except Exception as exc:
        raise AuthError(f"Invalid or expired child token: {exc}") from exc
