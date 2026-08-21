# 2026-08-21 — Alan — Claude Code

- **Model:** Claude Sonnet 5 (`claude-sonnet-5`)
- **Notes:** Alan asked to add token limits per account "once I connect to llm api."
  `backend/llm.py`'s provider layer already exists (ticket #67) but no `LLM_API_KEY` is
  configured anywhere, confirmed directly before responding. Laid out the design as
  prose (per-account cap, lifetime vs monthly, fallback behavior, where the counter
  lives) since it's a real product tradeoff, not a mechanical pick - Alan confirmed and
  added the actual driver: "for now mainly demo people" (the 10 demo accounts created
  earlier this session).

  Went through EnterPlanMode before touching code, copied the approved plan into
  `.claude/plans/llm-token-limit-per-account.md` per repo convention. Full TDD: new
  `generate_text_with_usage()` in `llm.py` (kept `generate_text()`'s return type
  unchanged so `rule_drafting.py` and its existing test mocks needed zero changes -
  only one new function, not a breaking rewrite), `parents.py` gained
  `has_reached_llm_token_limit`/`record_llm_tokens_used`, `hint_escalation_llm.py`
  wired both in as one more fallback reason (limit reached -> generic hint, same as a
  missing key or network error), `parent_id` threaded from `POST /attempts/check`'s
  already-resolved `Requester` through `run_pipeline` to the live hint call.

  New migration (`parents.llm_tokens_used`) applied directly to the live production
  project via the Supabase MCP `apply_migration` tool - no local Supabase CLI in this
  environment, and that's also where the demo accounts already live. Verified against
  a real demo account's row (family code RX7DPE): confirmed `LLM_TOKEN_LIMIT_PER_ACCOUNT=0`
  trips the limit immediately and the real default doesn't, then reset that account's
  counter back to 0 so the manual test didn't leave residue.

  Full backend suite green (307/307 including integration). Updated
  `docs/architecture/system-design.html`'s `PARENTS` ER block in the same PR, per the
  standing CLAUDE.md rule - checked proactively, not left for later.
