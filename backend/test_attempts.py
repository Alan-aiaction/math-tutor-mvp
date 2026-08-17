from unittest.mock import MagicMock, patch

import pytest
from postgrest.exceptions import APIError

from attempts import AttemptPersistenceError, create_attempt


def _mock_client_for(attempt_row, step_rows):
    mock_client = MagicMock()

    attempts_table = MagicMock()
    attempts_table.insert.return_value.execute.return_value.data = [attempt_row]

    steps_table = MagicMock()
    steps_table.insert.return_value.execute.return_value.data = step_rows

    def table(name):
        return {"attempts": attempts_table, "attempt_steps": steps_table}[name]

    mock_client.table.side_effect = table
    return mock_client


def test_successful_create_returns_attempt_with_generated_ids():
    attempt_row = {
        "id": 1,
        "problem_id": 5,
        "child_id": 42,
        "status": "in_progress",
        "created_at": "2026-08-16T00:00:00Z",
    }
    step_rows = [
        {"id": 10, "recognized_latex": "1/4 + 1/3", "is_correct": True, "previous_wrong_count": 0},
        {"id": 11, "recognized_latex": "7/12", "is_correct": True, "previous_wrong_count": 1},
    ]
    mock_client = _mock_client_for(attempt_row, step_rows)

    with patch("attempts.get_client", return_value=mock_client):
        result = create_attempt(
            problem_id=5,
            child_id=42,
            status="in_progress",
            steps=[
                {"recognized_latex": "1/4 + 1/3", "is_correct": True, "previous_wrong_count": 0},
                {"recognized_latex": "7/12", "is_correct": True, "previous_wrong_count": 1},
            ],
        )

    assert result.id == 1
    assert result.problem_id == 5
    assert result.created_at == "2026-08-16T00:00:00Z"
    assert len(result.steps) == 2
    assert result.steps[0].id == 10
    assert result.steps[0].attempt_id == 1
    assert result.steps[1].previous_wrong_count == 1


def test_step_previous_wrong_count_defaults_to_zero_when_omitted():
    attempt_row = {
        "id": 4,
        "problem_id": 5,
        "child_id": 42,
        "status": "in_progress",
        "created_at": "2026-08-16T00:00:00Z",
    }
    step_rows = [{"id": 12, "recognized_latex": "7/12", "is_correct": True, "previous_wrong_count": 0}]
    mock_client = _mock_client_for(attempt_row, step_rows)

    with patch("attempts.get_client", return_value=mock_client):
        result = create_attempt(
            problem_id=5,
            child_id=42,
            status="in_progress",
            steps=[{"recognized_latex": "7/12", "is_correct": True}],
        )

    assert result.steps[0].previous_wrong_count == 0


def test_no_steps_returns_attempt_with_empty_steps_list():
    attempt_row = {
        "id": 2,
        "problem_id": 5,
        "child_id": 42,
        "status": "in_progress",
        "created_at": "2026-08-16T00:00:00Z",
    }
    mock_client = _mock_client_for(attempt_row, [])

    with patch("attempts.get_client", return_value=mock_client):
        result = create_attempt(problem_id=5, child_id=42, status="in_progress", steps=[])

    assert result.id == 2
    assert result.steps == []


def test_invalid_problem_id_raises_attempt_persistence_error():
    mock_client = MagicMock()
    mock_client.table.return_value.insert.return_value.execute.side_effect = APIError(
        {"message": "insert or update on table violates foreign key constraint"}
    )

    with patch("attempts.get_client", return_value=mock_client):
        with pytest.raises(AttemptPersistenceError):
            create_attempt(problem_id=999999, child_id=42, status="in_progress", steps=[])


def test_steps_insert_failure_raises_attempt_persistence_error():
    attempt_row = {"id": 3, "problem_id": 5, "child_id": 42, "status": "in_progress"}
    mock_client = _mock_client_for(attempt_row, [])
    mock_client.table("attempt_steps").insert.return_value.execute.side_effect = APIError(
        {"message": "boom"}
    )

    with patch("attempts.get_client", return_value=mock_client):
        with pytest.raises(AttemptPersistenceError):
            create_attempt(
                problem_id=5,
                child_id=42,
                status="in_progress",
                steps=[{"recognized_latex": "7/12", "is_correct": True}],
            )
