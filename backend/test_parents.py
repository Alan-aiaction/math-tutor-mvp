"""Unit tests for parents.py (independent child login + child cap groundwork).
Mocked Supabase client, no real DB.
"""
from unittest.mock import MagicMock, patch

from parents import (
    DEFAULT_MAX_CHILDREN,
    _CODE_ALPHABET,
    _generate_family_code,
    get_or_create_parent,
    get_parent_by_family_code,
    has_reached_llm_token_limit,
    record_llm_tokens_used,
)

PARENT_ID = "11111111-1111-1111-1111-111111111111"


def test_get_or_create_parent_returns_existing_row_without_inserting():
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"id": PARENT_ID, "family_code": "AB12CD", "max_children": 3, "created_at": "2026-08-19T00:00:00Z"}
    ]
    with patch("parents.get_client", return_value=mock_client):
        result = get_or_create_parent(PARENT_ID)

    assert result.id == PARENT_ID
    assert result.family_code == "AB12CD"
    assert result.max_children == 3
    mock_client.table.return_value.insert.assert_not_called()


def test_get_or_create_parent_creates_a_new_row_with_a_generated_code_when_none_exists():
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    inserted = {}

    def insert(payload):
        inserted.update(payload)
        mock_result = MagicMock()
        mock_result.execute.return_value.data = [
            {
                "id": PARENT_ID,
                "family_code": payload["family_code"],
                "max_children": payload["max_children"],
                "created_at": "2026-08-19T00:00:00Z",
            }
        ]
        return mock_result

    mock_client.table.return_value.insert.side_effect = insert

    with patch("parents.get_client", return_value=mock_client):
        result = get_or_create_parent(PARENT_ID)

    assert result.id == PARENT_ID
    assert result.max_children == DEFAULT_MAX_CHILDREN
    assert len(inserted["family_code"]) == 6


def test_family_code_only_uses_unambiguous_characters():
    # A parent reads/writes this code out for a child by hand - 0/O/1/I/L are excluded
    # since they're the classic handwriting/read-aloud confusions.
    assert not set(_CODE_ALPHABET) & set("0O1IL")
    for _ in range(200):
        code = _generate_family_code()
        assert len(code) == 6
        assert all(c in _CODE_ALPHABET for c in code)


def test_get_or_create_parent_retries_on_family_code_collision():
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    call_count = {"n": 0}

    def insert(payload):
        call_count["n"] += 1
        mock_result = MagicMock()
        if call_count["n"] == 1:
            mock_result.execute.side_effect = Exception("duplicate key value violates unique constraint")
        else:
            mock_result.execute.return_value.data = [
                {
                    "id": PARENT_ID,
                    "family_code": payload["family_code"],
                    "max_children": DEFAULT_MAX_CHILDREN,
                    "created_at": "2026-08-19T00:00:00Z",
                }
            ]
        return mock_result

    mock_client.table.return_value.insert.side_effect = insert

    with patch("parents.get_client", return_value=mock_client):
        result = get_or_create_parent(PARENT_ID)

    assert call_count["n"] == 2
    assert result.id == PARENT_ID


# --- Independent child login: family-code lookup (PR 2 of 3) ---


def test_get_parent_by_family_code_returns_the_matching_parent():
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"id": PARENT_ID, "family_code": "AB12CD", "max_children": 3, "created_at": "2026-08-19T00:00:00Z"}
    ]
    with patch("parents.get_client", return_value=mock_client):
        result = get_parent_by_family_code("AB12CD")
    assert result is not None
    assert result.id == PARENT_ID


def test_get_parent_by_family_code_returns_none_when_not_found():
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    with patch("parents.get_client", return_value=mock_client):
        result = get_parent_by_family_code("NOTREAL")
    assert result is None


# --- LLM token limit (per-account, lifetime cap) ---


def _mock_client_with_parent(llm_tokens_used):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {
            "id": PARENT_ID,
            "family_code": "AB12CD",
            "max_children": 3,
            "llm_tokens_used": llm_tokens_used,
            "created_at": "2026-08-19T00:00:00Z",
        }
    ]
    return mock_client


def test_has_reached_llm_token_limit_is_false_below_the_limit(monkeypatch):
    monkeypatch.setenv("LLM_TOKEN_LIMIT_PER_ACCOUNT", "1000")
    mock_client = _mock_client_with_parent(500)
    with patch("parents.get_client", return_value=mock_client):
        assert has_reached_llm_token_limit(PARENT_ID) is False


def test_has_reached_llm_token_limit_is_true_at_the_limit(monkeypatch):
    monkeypatch.setenv("LLM_TOKEN_LIMIT_PER_ACCOUNT", "1000")
    mock_client = _mock_client_with_parent(1000)
    with patch("parents.get_client", return_value=mock_client):
        assert has_reached_llm_token_limit(PARENT_ID) is True


def test_has_reached_llm_token_limit_is_true_above_the_limit(monkeypatch):
    monkeypatch.setenv("LLM_TOKEN_LIMIT_PER_ACCOUNT", "1000")
    mock_client = _mock_client_with_parent(1500)
    with patch("parents.get_client", return_value=mock_client):
        assert has_reached_llm_token_limit(PARENT_ID) is True


def test_record_llm_tokens_used_adds_to_the_existing_count():
    mock_client = _mock_client_with_parent(500)
    with patch("parents.get_client", return_value=mock_client):
        record_llm_tokens_used(PARENT_ID, 150)

    mock_client.table.return_value.update.assert_called_once_with({"llm_tokens_used": 650})
