"""Unit tests for auth.py (3rd MVP). Mocked Supabase client, no real DB/auth-server call."""
from unittest.mock import MagicMock, patch

import pytest

from auth import AuthError, get_current_parent_id


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
