"""Parent authentication (3rd MVP).

Only the parent is a real Supabase Auth identity - the frontend signs a parent up/in
directly against Supabase (using the anon key, never routed through this backend), then
sends the resulting access token as a Bearer header on every request that needs to act on
behalf of that parent. This module verifies that token server-side and returns the
parent's real user id; it never issues or manages sessions itself.

Child accounts are deliberately NOT a second independent auth system - see children.py's
own docstring for why. This module only ever authenticates the parent.
"""
from db import get_client


class AuthError(Exception):
    """Raised when a request's Authorization header is missing, malformed, or the token
    it carries isn't a valid, current Supabase session - callers map this to 401."""


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
