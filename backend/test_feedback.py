"""Unit tests for feedback.py (feedback page). Mocked Supabase client, no real DB."""
from unittest.mock import MagicMock, patch

from feedback import create_feedback

PARENT_ID = "11111111-1111-1111-1111-111111111111"


def _mock_client_for_insert(inserted_row):
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [inserted_row]
    return mock_client


def test_create_feedback_inserts_a_parent_submission():
    row = {
        "id": 1,
        "parent_id": PARENT_ID,
        "child_id": None,
        "rating": 4,
        "category": "Bug",
        "message": "The check button was slow.",
        "created_at": "2026-08-22T00:00:00Z",
    }
    mock_client = _mock_client_for_insert(row)
    with patch("feedback.get_client", return_value=mock_client):
        result = create_feedback(PARENT_ID, None, 4, "Bug", "The check button was slow.")

    mock_client.table.return_value.insert.assert_called_once_with(
        {
            "parent_id": PARENT_ID,
            "child_id": None,
            "rating": 4,
            "category": "Bug",
            "message": "The check button was slow.",
        }
    )
    assert result.id == 1
    assert result.parent_id == PARENT_ID
    assert result.child_id is None
    assert result.rating == 4
    assert result.category == "Bug"
    assert result.message == "The check button was slow."


def test_create_feedback_inserts_a_child_submission_no_category():
    row = {
        "id": 2,
        "parent_id": PARENT_ID,
        "child_id": 7,
        "rating": 5,
        "category": None,
        "message": None,
        "created_at": "2026-08-22T00:00:00Z",
    }
    mock_client = _mock_client_for_insert(row)
    with patch("feedback.get_client", return_value=mock_client):
        result = create_feedback(PARENT_ID, 7, 5, None, None)

    assert result.child_id == 7
    assert result.category is None
    assert result.message is None
