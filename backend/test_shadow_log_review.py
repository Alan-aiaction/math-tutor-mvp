from unittest.mock import MagicMock, patch

from shadow_log_review import get_wrong_answer_clusters


def _mock_client_for(wrong_answer_rows, reviewed_rows=None):
    mock_client = MagicMock()

    def table_side_effect(name):
        table_mock = MagicMock()
        if name == "shadow_log_wrong_answers":
            table_mock.select.return_value.execute.return_value.data = wrong_answer_rows
            table_mock.select.return_value.eq.return_value.execute.return_value.data = wrong_answer_rows
        elif name == "shadow_log_review_notes":
            rows = reviewed_rows or []
            table_mock.select.return_value.execute.return_value.data = rows
            table_mock.select.return_value.eq.return_value.execute.return_value.data = rows
        return table_mock

    mock_client.table.side_effect = table_side_effect
    return mock_client


def _row(attempt_step_id, problem_id, student_answer, question_text="1/4 + 1/3", correct_answer="7/12"):
    return {
        "attempt_step_id": attempt_step_id,
        "student_answer": student_answer,
        "attempt_id": 1,
        "student_id": "test",
        "problem_id": problem_id,
        "question_text": question_text,
        "correct_answer": correct_answer,
    }


def test_equivalent_wrong_answers_cluster_together_even_when_text_differs():
    rows = [
        _row(1, 5, "2/7"),
        _row(2, 5, "2 / 7"),
    ]
    mock_client = _mock_client_for(rows)

    with patch("shadow_log_review.get_client", return_value=mock_client):
        clusters = get_wrong_answer_clusters()

    assert len(clusters) == 1
    assert clusters[0]["occurrence_count"] == 2
    assert clusters[0]["problem_id"] == 5
    assert set(clusters[0]["attempt_step_ids"]) == {1, 2}


def test_non_equivalent_wrong_answers_form_separate_clusters():
    rows = [
        _row(1, 5, "2/7"),
        _row(2, 5, "5/12"),
    ]
    mock_client = _mock_client_for(rows)

    with patch("shadow_log_review.get_client", return_value=mock_client):
        clusters = get_wrong_answer_clusters()

    assert len(clusters) == 2
    assert {c["occurrence_count"] for c in clusters} == {1, 1}


def test_unparseable_answers_form_their_own_parse_failed_cluster():
    rows = [
        _row(1, 5, "2/7"),
        _row(2, 5, "asdkfj not math"),
        _row(3, 5, "also garbled"),
    ]
    mock_client = _mock_client_for(rows)

    with patch("shadow_log_review.get_client", return_value=mock_client):
        clusters = get_wrong_answer_clusters()

    parse_failed = [c for c in clusters if c["parse_failed"]]
    parsed = [c for c in clusters if not c["parse_failed"]]
    assert len(parse_failed) == 1
    assert parse_failed[0]["occurrence_count"] == 2
    assert len(parsed) == 1
    assert parsed[0]["occurrence_count"] == 1


def test_clusters_sorted_by_occurrence_count_descending():
    rows = [
        _row(1, 5, "2/7"),
        _row(2, 5, "5/12"),
        _row(3, 5, "5/12"),
        _row(4, 5, "5/12"),
    ]
    mock_client = _mock_client_for(rows)

    with patch("shadow_log_review.get_client", return_value=mock_client):
        clusters = get_wrong_answer_clusters()

    assert [c["occurrence_count"] for c in clusters] == [3, 1]


def test_already_reviewed_cluster_excluded():
    rows = [_row(1, 5, "2/7")]
    reviewed = [{"problem_id": 5, "representative_answer": "2/7"}]
    mock_client = _mock_client_for(rows, reviewed_rows=reviewed)

    with patch("shadow_log_review.get_client", return_value=mock_client):
        clusters = get_wrong_answer_clusters()

    assert clusters == []


def test_clusters_grouped_independently_per_problem():
    rows = [
        _row(1, 5, "2/7", question_text="q5", correct_answer="7/12"),
        _row(2, 9, "2/7", question_text="q9", correct_answer="1/2"),
    ]
    mock_client = _mock_client_for(rows)

    with patch("shadow_log_review.get_client", return_value=mock_client):
        clusters = get_wrong_answer_clusters()

    assert len(clusters) == 2
    assert {c["problem_id"] for c in clusters} == {5, 9}
