"""Unit tests for hint_selection.py (ticket #33).

Mocked Supabase client, no real DB - same pattern as test_misconception_matching.py.
"""
from unittest.mock import MagicMock, patch

from generic_hint import get_generic_hint
from hint_selection import select_hint


def _mock_client_with_hints(hints):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = (
        hints
    )
    return mock_client


def test_none_misconception_id_returns_generic_hint_without_touching_db():
    # get_client is never patched here - if select_hint tried to call it for a None
    # id, this test would raise (no real Supabase credentials in a unit test run).
    assert select_hint(None) == get_generic_hint()


def test_no_approved_hint_for_this_misconception_falls_back_to_generic():
    with patch("hint_selection.get_client", return_value=_mock_client_with_hints([])):
        result = select_hint("some_misconception_id")
    assert result == get_generic_hint()


def test_single_approved_hint_is_returned():
    hint_row = {
        "id": "x_hint_1",
        "misconception_id": "x",
        "text": "Bijna goed! Probeer het nog eens.",
        "level": 1,
    }
    with patch("hint_selection.get_client", return_value=_mock_client_with_hints([hint_row])):
        result = select_hint("x")
    assert result == hint_row["text"]


def test_multiple_approved_hints_returns_one_of_them():
    hints = [
        {"id": "x_hint_1", "misconception_id": "x", "text": "Variant A", "level": 1},
        {"id": "x_hint_2", "misconception_id": "x", "text": "Variant B", "level": 1},
    ]
    with patch("hint_selection.get_client", return_value=_mock_client_with_hints(hints)):
        result = select_hint("x")
    assert result in {"Variant A", "Variant B"}


def test_varies_across_calls_not_always_the_first():
    """#70's own story: 'not the exact same sentence every time.' Not flaky - with
    2 options and enough draws, both must appear at least once."""
    hints = [
        {"id": "x_hint_1", "misconception_id": "x", "text": "Variant A", "level": 1},
        {"id": "x_hint_2", "misconception_id": "x", "text": "Variant B", "level": 1},
    ]
    with patch("hint_selection.get_client", return_value=_mock_client_with_hints(hints)):
        results = {select_hint("x") for _ in range(50)}
    assert results == {"Variant A", "Variant B"}
