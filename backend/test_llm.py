from unittest.mock import MagicMock, patch

import pytest
import requests

from llm import LLMError, generate_text, generate_text_with_usage


def _set_common_env(monkeypatch, provider, model="test-model", api_key="test-key"):
    monkeypatch.setenv("LLM_PROVIDER", provider)
    monkeypatch.setenv("LLM_API_KEY", api_key)
    monkeypatch.setenv("LLM_MODEL", model)


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_MODEL", "test-model")
    with pytest.raises(LLMError):
        generate_text("hello")


def test_missing_model_raises(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.delenv("LLM_MODEL", raising=False)
    with pytest.raises(LLMError):
        generate_text("hello")


def test_unknown_provider_raises(monkeypatch):
    _set_common_env(monkeypatch, "not-a-real-provider")
    with pytest.raises(LLMError):
        generate_text("hello")


def test_non_200_response_raises(monkeypatch):
    _set_common_env(monkeypatch, "anthropic")
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    with patch("llm.requests.post", return_value=mock_response):
        with pytest.raises(LLMError):
            generate_text("hello")


def test_network_timeout_raises(monkeypatch):
    _set_common_env(monkeypatch, "anthropic")
    with patch("llm.requests.post", side_effect=requests.exceptions.Timeout()):
        with pytest.raises(LLMError):
            generate_text("hello")


def test_anthropic_success_sends_expected_headers_and_returns_text(monkeypatch):
    _set_common_env(monkeypatch, "anthropic", model="claude-test", api_key="anthropic-key")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"content": [{"text": "hint text"}]}

    with patch("llm.requests.post", return_value=mock_response) as mock_post:
        result = generate_text("hello")

    assert result == "hint text"
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.anthropic.com/v1/messages"
    assert kwargs["headers"]["x-api-key"] == "anthropic-key"
    assert kwargs["json"]["model"] == "claude-test"


def test_openai_compatible_success_uses_default_base_url(monkeypatch):
    _set_common_env(monkeypatch, "openai_compatible", model="gpt-test", api_key="openai-key")
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "hint text"}}]}

    with patch("llm.requests.post", return_value=mock_response) as mock_post:
        result = generate_text("hello")

    assert result == "hint text"
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.openai.com/v1/chat/completions"
    assert kwargs["headers"]["Authorization"] == "Bearer openai-key"


def test_openai_compatible_uses_custom_base_url_for_openrouter(monkeypatch):
    _set_common_env(monkeypatch, "openai_compatible", model="meta-llama/llama-3.1-8b-instruct", api_key="or-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "hint text"}}]}

    with patch("llm.requests.post", return_value=mock_response) as mock_post:
        result = generate_text("hello")

    assert result == "hint text"
    args, _ = mock_post.call_args
    assert args[0] == "https://openrouter.ai/api/v1/chat/completions"


def test_openai_compatible_non_200_raises(monkeypatch):
    _set_common_env(monkeypatch, "openai_compatible")
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    with patch("llm.requests.post", return_value=mock_response):
        with pytest.raises(LLMError):
            generate_text("hello")


def test_generate_text_with_usage_returns_anthropic_token_count(monkeypatch):
    _set_common_env(monkeypatch, "anthropic")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "content": [{"text": "hint text"}],
        "usage": {"input_tokens": 120, "output_tokens": 30},
    }
    with patch("llm.requests.post", return_value=mock_response):
        result = generate_text_with_usage("hello")

    assert result.text == "hint text"
    assert result.tokens_used == 150


def test_generate_text_with_usage_returns_openai_compatible_token_count(monkeypatch):
    _set_common_env(monkeypatch, "openai_compatible")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "hint text"}}],
        "usage": {"prompt_tokens": 80, "completion_tokens": 20, "total_tokens": 100},
    }
    with patch("llm.requests.post", return_value=mock_response):
        result = generate_text_with_usage("hello")

    assert result.text == "hint text"
    assert result.tokens_used == 100


def test_generate_text_with_usage_defaults_to_zero_tokens_when_usage_missing(monkeypatch):
    # A provider response missing "usage" entirely shouldn't crash the call - it just
    # means nothing gets counted toward the account's limit this time.
    _set_common_env(monkeypatch, "anthropic")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"content": [{"text": "hint text"}]}
    with patch("llm.requests.post", return_value=mock_response):
        result = generate_text_with_usage("hello")

    assert result.text == "hint text"
    assert result.tokens_used == 0


def test_generate_text_ignores_usage_and_returns_plain_text(monkeypatch):
    # generate_text() is unchanged for rule_drafting.py's sake - still a plain string.
    _set_common_env(monkeypatch, "anthropic")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "content": [{"text": "hint text"}],
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }
    with patch("llm.requests.post", return_value=mock_response):
        result = generate_text("hello")

    assert result == "hint text"
