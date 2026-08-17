"""Unit tests for kpis.py. Mocked Supabase client, no real DB."""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from kpis import get_accuracy_trend, get_average_retries, get_practice_frequency, get_weak_spots_by_topic


def _mock_client(attempts=None, steps=None, problems=None):
    mock_client = MagicMock()

    attempts_table = MagicMock()
    attempts_table.select.return_value.eq.return_value.execute.return_value.data = attempts or []

    steps_table = MagicMock()
    steps_table.select.return_value.in_.return_value.execute.return_value.data = steps or []

    problems_table = MagicMock()
    problems_table.select.return_value.in_.return_value.execute.return_value.data = problems or []

    def table(name):
        return {"attempts": attempts_table, "attempt_steps": steps_table, "problems": problems_table}[name]

    mock_client.table.side_effect = table
    return mock_client


def test_get_accuracy_trend_groups_by_day():
    attempts = [
        {"id": 1, "problem_id": 100, "created_at": "2026-08-15T10:00:00+00:00"},
        {"id": 2, "problem_id": 100, "created_at": "2026-08-16T09:00:00+00:00"},
    ]
    steps = [
        {"attempt_id": 1, "is_correct": True, "previous_wrong_count": 0},
        {"attempt_id": 1, "is_correct": False, "previous_wrong_count": 1},
        {"attempt_id": 2, "is_correct": True, "previous_wrong_count": 0},
    ]
    mock_client = _mock_client(attempts=attempts, steps=steps)
    with patch("kpis.get_client", return_value=mock_client):
        result = get_accuracy_trend(child_id=1)

    assert result == [
        {"date": "2026-08-15", "accuracy": 0.5},
        {"date": "2026-08-16", "accuracy": 1.0},
    ]


def test_get_accuracy_trend_empty_when_no_attempts():
    with patch("kpis.get_client", return_value=_mock_client()):
        result = get_accuracy_trend(child_id=1)
    assert result == []


def test_get_average_retries_computes_mean():
    attempts = [{"id": 1}, {"id": 2}]
    steps = [
        {"previous_wrong_count": 0},
        {"previous_wrong_count": 2},
        {"previous_wrong_count": 4},
    ]
    mock_client = _mock_client(attempts=attempts, steps=steps)
    with patch("kpis.get_client", return_value=mock_client):
        result = get_average_retries(child_id=1)
    assert result == 2.0


def test_get_average_retries_zero_when_no_attempts():
    with patch("kpis.get_client", return_value=_mock_client()):
        result = get_average_retries(child_id=1)
    assert result == 0.0


def test_get_weak_spots_by_topic_sorts_weakest_first():
    attempts = [
        {"id": 1, "problem_id": 100, "created_at": "2026-08-15T10:00:00+00:00"},
        {"id": 2, "problem_id": 200, "created_at": "2026-08-16T09:00:00+00:00"},
    ]
    steps = [
        {"attempt_id": 1, "is_correct": False, "previous_wrong_count": 1},
        {"attempt_id": 2, "is_correct": True, "previous_wrong_count": 0},
    ]
    problems = [
        {"id": 100, "topic": "fractions"},
        {"id": 200, "topic": "percentages"},
    ]
    mock_client = _mock_client(attempts=attempts, steps=steps, problems=problems)
    with patch("kpis.get_client", return_value=mock_client):
        result = get_weak_spots_by_topic(child_id=1)

    assert result == [
        {"topic": "fractions", "accuracy": 0.0},
        {"topic": "percentages", "accuracy": 1.0},
    ]


def test_get_weak_spots_by_topic_empty_when_no_attempts():
    with patch("kpis.get_client", return_value=_mock_client()):
        result = get_weak_spots_by_topic(child_id=1)
    assert result == []


def test_get_practice_frequency_counts_distinct_recent_days_only():
    now = datetime.now(timezone.utc)
    day1 = now.isoformat()
    day2 = (now - timedelta(days=1)).isoformat()
    too_old = (now - timedelta(days=40)).isoformat()
    attempts = [
        {"created_at": day1},
        {"created_at": day1},  # same day as the row above - shouldn't double count
        {"created_at": day2},
        {"created_at": too_old},  # outside the default 30-day window
    ]
    mock_client = _mock_client(attempts=attempts)
    with patch("kpis.get_client", return_value=mock_client):
        result = get_practice_frequency(child_id=1)
    assert result == 2


def test_get_practice_frequency_zero_when_no_attempts():
    with patch("kpis.get_client", return_value=_mock_client()):
        result = get_practice_frequency(child_id=1)
    assert result == 0
