"""Unit tests for auth.py (3rd MVP + independent child login). Mocked Supabase client,
no real DB/auth-server call."""
import os
import time
from unittest.mock import MagicMock, patch

import jwt
import pytest

from auth import AuthError, get_current_child, get_current_parent_id, issue_child_token


def _mock_client_returning_user(user_id):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.user.id = user_id
    mock_client.auth.get_user.return_value = mock_response
    return mock_client


@pytest.mark.parametrize("header", [None, "", "not-a-bearer-token", "Bearer "])
def test_missing_or_malformed_header_raises_auth_error(header):
    with pytest.raises(AuthError):
        get_current_parent_id(header)


def test_valid_token_returns_the_users_id():
    with patch("auth.get_client", return_value=_mock_client_returning_user("parent-uuid-123")):
        result = get_current_parent_id("Bearer valid-token")
    assert result == "parent-uuid-123"


def test_supabase_rejecting_the_token_raises_auth_error():
    mock_client = MagicMock()
    mock_client.auth.get_user.side_effect = Exception("invalid JWT")
    with patch("auth.get_client", return_value=mock_client):
        with pytest.raises(AuthError):
            get_current_parent_id("Bearer expired-token")


def test_no_user_on_the_response_raises_auth_error():
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.user = None
    mock_client.auth.get_user.return_value = mock_response
    with patch("auth.get_client", return_value=mock_client):
        with pytest.raises(AuthError):
            get_current_parent_id("Bearer some-token")


# --- Independent child login: child session token (PR 2 of 3) ---


def test_issue_then_verify_child_token_round_trips():
    with patch.dict(os.environ, {"CHILD_SESSION_SECRET": "test-secret"}):
        token = issue_child_token(child_id=7, parent_id="parent-uuid-123")
        result = get_current_child(f"Bearer {token}")
    assert result.child_id == 7
    assert result.parent_id == "parent-uuid-123"


@pytest.mark.parametrize("header", [None, "", "not-a-bearer-token", "Bearer "])
def test_child_token_missing_or_malformed_header_raises_auth_error(header):
    with patch.dict(os.environ, {"CHILD_SESSION_SECRET": "test-secret"}):
        with pytest.raises(AuthError):
            get_current_child(header)


def test_child_token_signed_with_a_different_secret_raises_auth_error():
    with patch.dict(os.environ, {"CHILD_SESSION_SECRET": "test-secret"}):
        forged = jwt.encode(
            {"child_id": 7, "parent_id": "parent-uuid-123", "exp": int(time.time()) + 3600},
            "wrong-secret",
            algorithm="HS256",
        )
        with pytest.raises(AuthError):
            get_current_child(f"Bearer {forged}")


def test_expired_child_token_raises_auth_error():
    with patch.dict(os.environ, {"CHILD_SESSION_SECRET": "test-secret"}):
        expired = jwt.encode(
            {"child_id": 7, "parent_id": "parent-uuid-123", "exp": int(time.time()) - 60},
            "test-secret",
            algorithm="HS256",
        )
        with pytest.raises(AuthError):
            get_current_child(f"Bearer {expired}")


def test_a_parents_supabase_token_is_not_a_valid_child_token():
    # A real Supabase JWT is signed with Supabase's own key, not CHILD_SESSION_SECRET -
    # this just confirms the two token types can never be confused for one another.
    with patch.dict(os.environ, {"CHILD_SESSION_SECRET": "test-secret"}):
        not_a_child_token = jwt.encode({"sub": "parent-uuid-123"}, "some-other-key", algorithm="HS256")
        with pytest.raises(AuthError):
            get_current_child(f"Bearer {not_a_child_token}")
