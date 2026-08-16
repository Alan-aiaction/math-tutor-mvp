"""Unit tests for children.py (3rd MVP). Mocked Supabase client, no real DB."""
from unittest.mock import MagicMock, patch

import bcrypt

from children import ChildError, create_child, get_child, list_children, verify_child_login

PARENT_ID = "11111111-1111-1111-1111-111111111111"
OTHER_PARENT_ID = "22222222-2222-2222-2222-222222222222"


def _mock_client_with_rows(rows):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = rows
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = (
        rows
    )
    return mock_client


def test_create_child_hashes_the_password_not_stored_plaintext():
    mock_client = MagicMock()
    inserted = {}

    def insert(payload):
        inserted.update(payload)
        mock_result = MagicMock()
        mock_result.execute.return_value.data = [
            {"id": 1, "parent_id": PARENT_ID, "nickname": "Sam", "created_at": "2026-08-16T00:00:00Z"}
        ]
        return mock_result

    mock_client.table.return_value.insert.side_effect = insert

    with patch("children.get_client", return_value=mock_client):
        result = create_child(PARENT_ID, "Sam", "sesame")

    assert result.id == 1
    assert result.nickname == "Sam"
    assert inserted["password_hash"] != "sesame"
    assert bcrypt.checkpw(b"sesame", inserted["password_hash"].encode("utf-8"))


def test_create_child_raises_child_error_on_db_failure():
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.side_effect = Exception(
        "duplicate key value violates unique constraint"
    )
    with patch("children.get_client", return_value=mock_client):
        try:
            create_child(PARENT_ID, "Sam", "sesame")
            assert False, "expected ChildError"
        except ChildError:
            pass


def test_list_children_returns_only_this_parents_children():
    rows = [{"id": 1, "parent_id": PARENT_ID, "nickname": "Sam", "created_at": "2026-08-16T00:00:00Z"}]
    with patch("children.get_client", return_value=_mock_client_with_rows(rows)):
        result = list_children(PARENT_ID)
    assert len(result) == 1
    assert result[0].nickname == "Sam"


def test_list_children_empty_when_parent_has_none():
    with patch("children.get_client", return_value=_mock_client_with_rows([])):
        result = list_children(PARENT_ID)
    assert result == []


def test_get_child_returns_none_when_not_owned_by_this_parent():
    # Mocked client doesn't actually filter (same convention as this repo's other mock
    # helpers) - this test asserts the empty-rows case, which is what a real .eq()
    # ownership mismatch produces.
    with patch("children.get_client", return_value=_mock_client_with_rows([])):
        result = get_child(OTHER_PARENT_ID, 1)
    assert result is None


def test_get_child_returns_the_child_when_owned():
    rows = [{"id": 1, "parent_id": PARENT_ID, "nickname": "Sam", "created_at": "2026-08-16T00:00:00Z"}]
    with patch("children.get_client", return_value=_mock_client_with_rows(rows)):
        result = get_child(PARENT_ID, 1)
    assert result is not None
    assert result.nickname == "Sam"


def test_verify_child_login_correct_password():
    password_hash = bcrypt.hashpw(b"sesame", bcrypt.gensalt()).decode("utf-8")
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {"password_hash": password_hash}
    ]
    with patch("children.get_client", return_value=mock_client):
        assert verify_child_login(PARENT_ID, 1, "sesame") is True


def test_verify_child_login_wrong_password():
    password_hash = bcrypt.hashpw(b"sesame", bcrypt.gensalt()).decode("utf-8")
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [
        {"password_hash": password_hash}
    ]
    with patch("children.get_client", return_value=mock_client):
        assert verify_child_login(PARENT_ID, 1, "wrong-password") is False


def test_verify_child_login_not_this_parents_child():
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = (
        []
    )
    with patch("children.get_client", return_value=mock_client):
        assert verify_child_login(OTHER_PARENT_ID, 1, "sesame") is False
