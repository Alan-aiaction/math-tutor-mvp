from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app
from recognition import RecognitionError

# raise_server_exceptions=False: without this, TestClient re-raises the original
# exception for debugging convenience, even though the app's own exception handler
# already produced a response - we need to inspect that actual HTTP response here.
client = TestClient(app, raise_server_exceptions=False)


def test_unhandled_exception_returns_clean_500_not_a_crash():
    with patch("main.recognize_math", side_effect=RuntimeError("boom")):
        response = client.post(
            "/recognize",
            json={"strokeGroups": [], "width": 100, "height": 100},
        )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}


def test_recognition_error_still_maps_to_502_not_shadowed_by_global_handler():
    with patch("main.recognize_math", side_effect=RecognitionError("bad creds")):
        response = client.post(
            "/recognize",
            json={"strokeGroups": [], "width": 100, "height": 100},
        )
    assert response.status_code == 502


def test_request_logging_middleware_logs_method_path_status(caplog):
    with caplog.at_level("INFO", logger="main"):
        response = client.get("/health")
    assert response.status_code == 200
    matching = [r for r in caplog.records if "GET" in r.message and "/health" in r.message]
    assert len(matching) == 1
    assert "200" in matching[0].message


def test_check_attempt_correct_step():
    response = client.post(
        "/attempts/check",
        json={"steps": [{"recognized_latex": "7/12"}], "correct_answer": "7/12"},
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["valid"] is True
    assert results[0]["hint_text"] is None


def test_check_attempt_incorrect_step_gets_hint():
    response = client.post(
        "/attempts/check",
        json={"steps": [{"recognized_latex": "5/7"}], "correct_answer": "7/12"},
    )
    assert response.status_code == 200
    results = response.json()
    assert results[0]["valid"] is False
    assert results[0]["hint_text"]


def test_check_attempt_multiple_steps_returns_one_result_each():
    response = client.post(
        "/attempts/check",
        json={
            "steps": [{"recognized_latex": "5/7"}, {"recognized_latex": "7/12"}],
            "correct_answer": "7/12",
        },
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_check_attempt_malformed_correct_answer_returns_400():
    response = client.post(
        "/attempts/check",
        json={"steps": [{"recognized_latex": "7/12"}], "correct_answer": r"\notacommand{x}"},
    )
    assert response.status_code == 400
