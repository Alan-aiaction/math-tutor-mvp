from unittest.mock import MagicMock, patch

import pytest

from db import DatabaseError, get_client


def test_missing_url_raises(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")
    with pytest.raises(DatabaseError):
        get_client()


def test_missing_service_role_key_raises(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    with pytest.raises(DatabaseError):
        get_client()


def test_successful_client_creation_returns_client(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")

    mock_client = MagicMock()
    with patch("db.create_client", return_value=mock_client) as mock_create:
        result = get_client()

    assert result is mock_client
    mock_create.assert_called_once_with("https://example.supabase.co", "test-key")


def test_create_client_failure_raises_and_logs(monkeypatch, caplog):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-key")

    with patch("db.create_client", side_effect=RuntimeError("connection refused")):
        with pytest.raises(DatabaseError):
            with caplog.at_level("ERROR"):
                get_client()

    assert "connection refused" in caplog.text
