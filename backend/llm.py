"""LLM provider-abstraction layer (ticket #67, 2nd MVP).

Every LLM-touching feature (rule drafting, hint authoring, live hint-phrasing) calls
generate_text() here - never a vendor SDK or a vendor's wire format directly. Provider,
model, and (for openai_compatible) base URL are config choices (LLM_PROVIDER, LLM_MODEL,
LLM_BASE_URL env vars), so switching later - including to a cheaper or open-weight model
via OpenRouter, Hugging Face's router, Together.ai, Groq, DeepSeek, Moonshot's Kimi, or a
self-hosted vLLM/Ollama server - is a config change, not a rewrite of every caller. All of
those speak the same OpenAI Chat Completions wire format, so one implementation
(openai_compatible) covers all of them, not just OpenAI itself.

Follows this codebase's existing pattern for wrapping an external paid API
(recognition.py): plain requests calls, no vendor SDK dependency, a module-level custom
exception, env-driven credentials.
"""
import os
from dataclasses import dataclass

import requests

REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_OPENAI_COMPATIBLE_BASE_URL = "https://api.openai.com/v1"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"


class LLMError(Exception):
    """Raised when an LLM call fails (missing config, unknown provider, timeout,
    or a non-200 response), instead of letting the failure crash the caller."""


@dataclass
class LLMResponse:
    """generate_text_with_usage()'s return shape - the generated text plus how many
    tokens the call actually cost, for callers (hint_escalation_llm.py's per-account
    token limit) that need to meter usage. generate_text() itself stays text-only for
    callers (rule_drafting.py) that don't."""

    text: str
    tokens_used: int


def _call_anthropic(prompt: str, *, api_key: str, model: str, max_tokens: int, temperature: float) -> tuple[str, int]:
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "Content-Type": "application/json",
    }
    response = requests.post(
        ANTHROPIC_API_URL, json=body, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
    )
    if response.status_code != 200:
        raise LLMError(f"anthropic API returned {response.status_code}: {response.text[:300]}")
    payload = response.json()
    usage = payload.get("usage", {})
    tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
    return payload["content"][0]["text"], tokens_used


def _call_openai_compatible(
    prompt: str, *, api_key: str, model: str, max_tokens: int, temperature: float
) -> tuple[str, int]:
    base_url = os.environ.get("LLM_BASE_URL", DEFAULT_OPENAI_COMPATIBLE_BASE_URL).rstrip("/")
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(
        f"{base_url}/chat/completions", json=body, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
    )
    if response.status_code != 200:
        raise LLMError(f"openai_compatible API returned {response.status_code}: {response.text[:300]}")
    payload = response.json()
    tokens_used = payload.get("usage", {}).get("total_tokens", 0)
    return payload["choices"][0]["message"]["content"], tokens_used


_PROVIDERS = {
    "anthropic": _call_anthropic,
    "openai_compatible": _call_openai_compatible,
}


def generate_text_with_usage(prompt: str, *, max_tokens: int = 512, temperature: float = 0.7) -> LLMResponse:
    """Generate text from the configured LLM provider, along with how many tokens the
    call cost.

    Raises LLMError on missing config, an unknown provider, or any request failure.
    """
    provider = os.environ.get("LLM_PROVIDER", "anthropic")
    api_key = os.environ.get("LLM_API_KEY")
    model = os.environ.get("LLM_MODEL")

    if provider not in _PROVIDERS:
        raise LLMError(f"Unknown LLM provider: {provider}")
    if not api_key:
        raise LLMError("LLM_API_KEY is not configured")
    if not model:
        raise LLMError("LLM_MODEL is not configured")

    try:
        text, tokens_used = _PROVIDERS[provider](
            prompt, api_key=api_key, model=model, max_tokens=max_tokens, temperature=temperature
        )
        return LLMResponse(text=text, tokens_used=tokens_used)
    except LLMError:
        raise
    except requests.exceptions.RequestException as exc:
        raise LLMError(f"{provider} request failed: {exc}") from exc


def generate_text(prompt: str, *, max_tokens: int = 512, temperature: float = 0.7) -> str:
    """Generate text from the configured LLM provider - the plain-text-only form used
    by callers (rule_drafting.py) that don't need token usage.

    Raises LLMError on missing config, an unknown provider, or any request failure.
    """
    return generate_text_with_usage(prompt, max_tokens=max_tokens, temperature=temperature).text
