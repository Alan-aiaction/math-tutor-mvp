"""Unit tests for children.py (3rd MVP). Mocked Supabase client, no real DB."""
from unittest.mock import MagicMock, patch

import bcrypt

from children import (
    ChildError,
    create_child,
    delete_child,
    get_child,
    get_child_by_nickname,
    list_children,
    verify_child_login,
)

PARENT_ID = "11111111-1111-1111-1111-111111111111"
OTHER_PARENT_ID = "22222222-2222-2222-2222-222222222222"

DEFAULT_PARENT_ROW = {"id": PARENT_ID, "family_code": "AB12CD", "max_children": 3, "created_at": "2026-08-16T00:00:00Z"}


def _mock_client_with_rows(rows):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = rows
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = (
        rows
    )
    return mock_client


def _mock_client_for_create(parent_row, existing_children_rows, insert_side_effect):
    """create_child now checks the child cap first (parents table lookup + a count of
    existing children), then inserts - so this mock has to dispatch by table name
    rather than reuse a single `.table.return_value` like the simpler helper above."""
    mock_client = MagicMock()

    parents_table = MagicMock()
    parents_table.select.return_value.eq.return_value.execute.return_value.data = (
        [parent_row] if parent_row else []
    )

    children_table = MagicMock()
    children_table.select.return_value.eq.return_value.execute.return_value.data = existing_children_rows
    children_table.insert.side_effect = insert_side_effect

    def table(name):
        return {"parents": parents_table, "children": children_table}[name]

    mock_client.table.side_effect = table
    return mock_client


def test_create_child_hashes_the_password_not_stored_plaintext():
    inserted = {}

    def insert(payload):
        inserted.update(payload)
        mock_result = MagicMock()
        mock_result.execute.return_value.data = [
            {"id": 1, "parent_id": PARENT_ID, "nickname": "Sam", "created_at": "2026-08-16T00:00:00Z"}
        ]
        return mock_result

    mock_client = _mock_client_for_create(DEFAULT_PARENT_ROW, existing_children_rows=[], insert_side_effect=insert)

    with patch("children.get_client", return_value=mock_client), patch("parents.get_client", return_value=mock_client):
        result = create_child(PARENT_ID, "Sam", "sesame")

    assert result.id == 1
    assert result.nickname == "Sam"
    assert inserted["password_hash"] != "sesame"
    assert bcrypt.checkpw(b"sesame", inserted["password_hash"].encode("utf-8"))


def test_create_child_raises_child_error_on_db_failure():
    def insert(payload):
        mock_result = MagicMock()
        mock_result.execute.side_effect = Exception("duplicate key value violates unique constraint")
        return mock_result

    mock_client = _mock_client_for_create(DEFAULT_PARENT_ROW, existing_children_rows=[], insert_side_effect=insert)

    with patch("children.get_client", return_value=mock_client), patch("parents.get_client", return_value=mock_client):
        try:
            create_child(PARENT_ID, "Sam", "sesame")
            assert False, "expected ChildError"
        except ChildError:
            pass


def test_create_child_raises_child_error_when_parent_is_at_the_cap():
    at_cap_parent = {"id": PARENT_ID, "family_code": "AB12CD", "max_children": 1, "created_at": "2026-08-16T00:00:00Z"}
    existing = [{"id": 1, "parent_id": PARENT_ID, "nickname": "Sam", "created_at": "2026-08-16T00:00:00Z"}]

    def insert(payload):
        raise AssertionError("insert should never be called once the cap is already reached")

    mock_client = _mock_client_for_create(at_cap_parent, existing_children_rows=existing, insert_side_effect=insert)

    with patch("children.get_client", return_value=mock_client), patch("parents.get_client", return_value=mock_client):
        try:
            create_child(PARENT_ID, "Odin", "sesame")
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


def _mock_client_for_delete(owned_rows, attempt_rows):
    """children table returns owned_rows for the ownership check, attempts returns
    attempt_rows for this child's attempt ids - both tables also need working
    .delete() chains so delete_child's cascade calls don't blow up on a bare
    MagicMock attribute access."""
    mock_client = MagicMock()

    children_table = MagicMock()
    children_table.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = owned_rows

    attempts_table = MagicMock()
    attempts_table.select.return_value.eq.return_value.execute.return_value.data = attempt_rows

    steps_table = MagicMock()

    def table(name):
        return {"children": children_table, "attempts": attempts_table, "attempt_steps": steps_table}[name]

    mock_client.table.side_effect = table
    return mock_client, children_table, attempts_table, steps_table


def test_delete_child_cascades_steps_then_attempts_then_child():
    owned_rows = [{"id": 1}]
    attempt_rows = [{"id": 10}, {"id": 11}]
    mock_client, children_table, attempts_table, steps_table = _mock_client_for_delete(owned_rows, attempt_rows)

    with patch("children.get_client", return_value=mock_client):
        result = delete_child(PARENT_ID, 1)

    assert result is True
    steps_table.delete.return_value.in_.assert_called_once_with("attempt_id", [10, 11])
    attempts_table.delete.return_value.eq.assert_called_once_with("child_id", 1)
    children_table.delete.return_value.eq.return_value.eq.assert_called_once_with("parent_id", PARENT_ID)


def test_delete_child_no_attempts_skips_step_delete_but_still_removes_child():
    mock_client, children_table, attempts_table, steps_table = _mock_client_for_delete([{"id": 1}], [])

    with patch("children.get_client", return_value=mock_client):
        result = delete_child(PARENT_ID, 1)

    assert result is True
    steps_table.delete.assert_not_called()
    children_table.delete.return_value.eq.return_value.eq.assert_called_once_with("parent_id", PARENT_ID)


def test_delete_child_not_owned_returns_false_and_deletes_nothing():
    mock_client, children_table, attempts_table, steps_table = _mock_client_for_delete([], [])

    with patch("children.get_client", return_value=mock_client):
        result = delete_child(OTHER_PARENT_ID, 1)

    assert result is False
    children_table.delete.assert_not_called()
    attempts_table.delete.assert_not_called()
    steps_table.delete.assert_not_called()


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


# --- Independent child login: nickname lookup (PR 2 of 3) ---


def test_get_child_by_nickname_returns_the_matching_child():
    rows = [{"id": 1, "parent_id": PARENT_ID, "nickname": "Sam", "created_at": "2026-08-16T00:00:00Z"}]
    with patch("children.get_client", return_value=_mock_client_with_rows(rows)):
        result = get_child_by_nickname(PARENT_ID, "Sam")
    assert result is not None
    assert result.id == 1


def test_get_child_by_nickname_returns_none_when_not_found():
    with patch("children.get_client", return_value=_mock_client_with_rows([])):
        result = get_child_by_nickname(PARENT_ID, "NotReal")
    assert result is None
