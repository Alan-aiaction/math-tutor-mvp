"""Unit tests for parents.py (independent child login + child cap groundwork).
Mocked Supabase client, no real DB.
"""
from unittest.mock import MagicMock, patch

from parents import DEFAULT_MAX_CHILDREN, _CODE_ALPHABET, _generate_family_code, get_or_create_parent

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
