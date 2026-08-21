-- Per-account lifetime LLM token limit (plan: llm-token-limit-per-account.md).
--
-- Tracks how many tokens this account's live LLM hint calls (hint_escalation_llm.py,
-- ticket #72) have cost in total, compared against LLM_TOKEN_LIMIT_PER_ACCOUNT
-- (backend/parents.py) before each live call. A flat lifetime cap, not a monthly
-- rolling one - this is pre-billing, invite-only testing (mainly the 10 demo
-- accounts), so there's no subscription period to reset against yet. Existing rows
-- default to 0, matching every account's real usage today (no LLM_API_KEY is
-- configured, so no live call has ever run).

alter table parents add column llm_tokens_used integer not null default 0;
