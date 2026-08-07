from unittest.mock import MagicMock, patch

import pytest

from problems import ProblemNotFoundError, get_problem


def _mock_client_for(rows):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = rows
    return mock_client


def test_get_problem_returns_problem_when_found():
    row = {
        "id": 5,
        "topic": "fractions",
        "difficulty": 2,
        "question_text": "1/4 + 1/3",
        "correct_answer": "7/12",
        "solving_tip": None,
    }
    mock_client = _mock_client_for([row])

    with patch("problems.get_client", return_value=mock_client):
        result = get_problem(5)

    assert result.id == 5
    assert result.topic == "fractions"
    assert result.correct_answer == "7/12"


def test_get_problem_raises_not_found_when_no_rows():
    mock_client = _mock_client_for([])

    with patch("problems.get_client", return_value=mock_client):
        with pytest.raises(ProblemNotFoundError):
            get_problem(999999)
