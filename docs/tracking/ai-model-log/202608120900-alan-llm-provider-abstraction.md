# 2026-08-12 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Session covering: implemented ticket #67, the first 2nd MVP ticket -
  backend/llm.py, a provider-abstraction layer for every future LLM-touching feature
  (rule/hint authoring, live hint escalation). Two real providers: anthropic (native
  Messages API) and openai_compatible (generic OpenAI Chat Completions wire format with
  configurable LLM_BASE_URL - covers OpenAI, OpenRouter, Hugging Face's router,
  Together.ai, Groq, DeepSeek, Moonshot/Kimi, and self-hosted vLLM/Ollama with zero new
  code, since they all speak the same wire format). Config-driven via
  LLM_PROVIDER/LLM_API_KEY/LLM_MODEL/LLM_BASE_URL, added to .env.example. Followed
  recognition.py's existing pattern for wrapping an external paid API (plain requests
  calls, no vendor SDK, module-level custom exception, mocked-only tests - no real-API
  integration test, matching that same precedent). 9 new unit tests in test_llm.py, full
  backend suite 112 passed (up from 103), zero regressions.
