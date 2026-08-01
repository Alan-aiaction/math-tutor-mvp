import hashlib
import hmac as hmac_lib
from unittest.mock import MagicMock, patch

import pytest
import requests

from recognition import RecognitionError, _compute_hmac, recognize_math

SAMPLE_STROKE_GROUPS = [{"penStyle": None, "strokes": [{"x": [1, 2], "y": [1, 2], "t": [1, 2]}]}]


def test_missing_credentials_raises(monkeypatch):
    monkeypatch.delenv("MYSCRIPT_APP_KEY", raising=False)
    monkeypatch.delenv("MYSCRIPT_HMAC_KEY", raising=False)
    with pytest.raises(RecognitionError):
        recognize_math(SAMPLE_STROKE_GROUPS, width=100, height=100)


def test_successful_recognition_returns_latex(monkeypatch):
    monkeypatch.setenv("MYSCRIPT_APP_KEY", "test-app-key")
    monkeypatch.setenv("MYSCRIPT_HMAC_KEY", "test-hmac-key")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = r"\frac{1}{2}"

    with patch("recognition.requests.post", return_value=mock_response) as mock_post:
        result = recognize_math(SAMPLE_STROKE_GROUPS, width=100, height=100)

    assert result == r"\frac{1}{2}"
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["applicationKey"] == "test-app-key"
    assert kwargs["headers"]["Accept"] == "application/x-latex"


def test_non_200_response_raises(monkeypatch):
    monkeypatch.setenv("MYSCRIPT_APP_KEY", "test-app-key")
    monkeypatch.setenv("MYSCRIPT_HMAC_KEY", "test-hmac-key")

    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"

    with patch("recognition.requests.post", return_value=mock_response):
        with pytest.raises(RecognitionError):
            recognize_math(SAMPLE_STROKE_GROUPS, width=100, height=100)


def test_network_timeout_raises(monkeypatch):
    monkeypatch.setenv("MYSCRIPT_APP_KEY", "test-app-key")
    monkeypatch.setenv("MYSCRIPT_HMAC_KEY", "test-hmac-key")

    with patch("recognition.requests.post", side_effect=requests.exceptions.Timeout()):
        with pytest.raises(RecognitionError):
            recognize_math(SAMPLE_STROKE_GROUPS, width=100, height=100)


def test_hmac_computation_is_deterministic_and_correct():
    h1 = _compute_hmac("app", "hmac", "body")
    h2 = _compute_hmac("app", "hmac", "body")
    assert h1 == h2
    expected = hmac_lib.new(b"apphmac", b"body", hashlib.sha512).hexdigest()
    assert h1 == expected
