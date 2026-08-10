from unittest.mock import MagicMock, patch

import pytest

from problems import ProblemNotFoundError, get_problem, get_random_problem


def _mock_client_for(rows):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = rows
    return mock_client


def _mock_client_for_random(id_rows, full_rows_by_id):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = id_rows

    def eq_side_effect(_field, value):
        result = MagicMock()
        result.execute.return_value.data = full_rows_by_id.get(value, [])
        return result

    mock_client.table.return_value.select.return_value.eq.side_effect = eq_side_effect
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


def test_get_random_problem_returns_one_of_the_seeded_rows():
    id_rows = [{"id": 5}, {"id": 6}, {"id": 7}]
    full_rows_by_id = {
        5: [{"id": 5, "topic": "fractions", "difficulty": 2, "question_text": "1/4 + 1/3", "correct_answer": "7/12", "solving_tip": None}],
        6: [{"id": 6, "topic": "fractions", "difficulty": 1, "question_text": "1/2 + 1/2", "correct_answer": "1", "solving_tip": None}],
        7: [{"id": 7, "topic": "fractions", "difficulty": 1, "question_text": "1/3 + 1/3", "correct_answer": "2/3", "solving_tip": None}],
    }
    mock_client = _mock_client_for_random(id_rows, full_rows_by_id)

    with patch("problems.get_client", return_value=mock_client):
        result = get_random_problem()

    assert result.id in {5, 6, 7}


def test_get_random_problem_raises_not_found_when_table_empty():
    mock_client = _mock_client_for_random([], {})

    with patch("problems.get_client", return_value=mock_client):
        with pytest.raises(ProblemNotFoundError):
            get_random_problem()
