# AI Tool/Model Log — historical, frozen as of 2026-08-06

**New entries no longer go in this file.** Every PR appending a row here was landing on the
same few lines, so any two PRs open at the same time reliably conflicted with each other —
happened repeatedly in practice, not hypothetically. As of 2026-08-06, each work session gets
its own new file in `docs/tracking/ai-model-log/` instead (see that folder's `README.md` for
the convention) — two new files can never collide, so this removes the conflict source
entirely. This file's existing rows stay exactly as they are, untouched, as the historical
record up to the cutover.

---

Tracks who was working, with which AI tool and model, and when — for provenance and
auditing. Not Claude-specific: Jeff/Richard may use a different AI tool (Copilot, Cursor,
ChatGPT, etc.) or none at all — log whatever's actually true. Append-only: never edit or
delete past entries.

**For Claude Code sessions specifically**: this is maintained automatically per the
instructions in `CLAUDE.md`. **For any other tool** (or no AI): please add a row by hand
when you do a substantial chunk of AI-assisted work, or note "Human, no AI" if that's
what happened — your tool won't know this file exists otherwise.

| Date | User | Tool | Model | Model ID | Notes |
|---|---|---|---|---|---|
| 2026-08-02 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: #17 ink capture, #18/#19 recognition wrapper + endpoint, #22-24 parser chain, Railway deploy verification (#56), API contract approval (#11), team onboarding docs (README, run-dev.ps1, CLAUDE.md local-dev section) |
| 2026-08-02 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: audited task-board.html + task-tracker.xlsx against merged GitHub PRs and actual code, corrected #17/#18/#19 from "Not started" to "Done" (AC-verified), added docs/Architecture.md noting the diagram's stale "+ confidence" text |
| 2026-08-03 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: planned #50 (student access code) and #6 (Supabase schema, incl. new solving_tip field from groep8 CSV review), added docs/system-design.html (data flow, interfaces, schema, decision logic, lifecycle, open-gaps tracker) |
| 2026-08-03 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: implemented #6 (docs/architecture/database_schema.sql), updated API contract with solving_tip and matching_rule (jsonb) fields, added docs/tracking/decision-log.md seeded with 6 decisions, reorganized docs/ into architecture/tracking/content subfolders |
| 2026-08-03 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: connected the Supabase MCP server and used it to implement #7 - applied the initial schema migration to the live project, verified FK constraints with a manual test insert, committed supabase/migrations/20260803120000_initial_schema.sql |
| 2026-08-03 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: #29 rule format proposal (docs/architecture/proposal_misconception_rule_format.md, diagram-based), scoping decision to defer #30/#9 implementation to a 2nd MVP while keeping #25-28/#34 and pulling shadow logging into the 1st, recorded in decision-log.md |
| 2026-08-03 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: cross-checked the task board against this session's scoping decisions, fixed #34's stale dependency on the deferred #33/#9 chain, added #63 (make shadow-logged wrong answers queryable) as its own ticket |
| 2026-08-04 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: added a CLAUDE.md working-style rule requiring every plan to open with "What this unlocks" before its Context section, so plans lead with tangible outcome, not just AC bullets |
| 2026-08-04 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: implemented #12 - added backend/models.py with the 6 contract domain models, verified all 3 AC bullets including actually starting uvicorn locally and hitting /health |
| 2026-08-04 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: implemented #13 (backend/db.py Supabase client + get_client()), added backend/test_db.py and backend/test_db_integration.py, discovered and fixed a live infra gap (service_role had zero table grants since #7's migration) via a Supabase migration, added missing pytest pin to requirements.txt |
| 2026-08-04 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: designed a full test-pyramid (70/20/10 unit/integration/E2E) test suite for backend + frontend plus a GitHub Actions CI mapping (no code written) - confirmed out of 1st MVP scope, logged as a deferred decision in docs/tracking/decision-log.md, design saved locally at .claude/plans/test-pyramid-design.md |
| 2026-08-04 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: added a CLAUDE.md "Test Pyramid" rule (new pure logic → unit test, new I/O-touching code → integration test against a real instance, ask before adding E2E, public-interface-only assertions) - applies to backend now, frontend waits on a test framework decision |
| 2026-08-04 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: expanded decision-log.md's [Living] entry from a top-5 pick to the full 1st MVP task order (33 remaining tickets, dependency-ordered, no owners), excluding the 2nd-MVP-deferred misconception chain; flagged #35 and #20 as needing the same dependency fix #34 got |
| 2026-08-05 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: implemented #10 (permissive Supabase RLS policies + matching GRANTs for anon/authenticated on all 5 tables), applied via Supabase migration and committed to supabase/migrations/, verified via pg_policies/role_table_grants/get_advisors, found #13's grant migration was never mirrored to a local file (flagged, not fixed) |
| 2026-08-05 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: implemented #25 (backend/expression_validity.py, is_valid_expression() - second gate on parsed SymPy expressions, rejects Relational/boolean/nan/zoo/infinities/complex results, never raises), 14 new test cases in backend/test_expression_validity.py |
| 2026-08-05 | Alan | Claude Code | Claude Sonnet 5 | `claude-sonnet-5` | Session covering: verified #47 (HTTPS enforcement) live against the deployed Railway backend and Vercel frontend - both redirect plain HTTP to HTTPS, no code change needed |
