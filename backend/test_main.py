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
