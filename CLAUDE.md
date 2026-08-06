# Repo Instructions for Claude

This file is read automatically by Claude Code / Claude Cowork when working in this repo.
Follow these rules for every change, without needing to be asked each time.

## Branch & PR workflow — non-negotiable

- **Never push directly to `main`.** Always create a branch first.
- Branch naming: `feature/short-description` or `fix/short-description`.
- Open a Pull Request for every change, however small.
- After opening a PR, give a short summary (a few sentences, ready to paste as-is into
  team chat) covering what changed and why — don't assume the team will read the full diff.
- Do not merge your own PR — wait for at least one teammate to review, or explicitly ask
  the user to confirm merge if working solo in a session.
- If asked to "fix X" or "add Y" directly on `main`, create a branch and PR instead, and
  tell the user you did so.
- **Stacked PRs (a branch based on another open PR's branch, not `main`) are a merge-order
  trap.** If PR B is based on PR A's branch, merging B into A's branch *after* A has already
  been merged into `main` does **not** bring B's changes into `main` — they land on a branch
  that's now disconnected from `main`'s history, even though GitHub shows B as "Merged."
  Always retarget a stacked PR's base to `main` once the PR(s) underneath it have merged,
  *before* merging it — don't merge it into its original (now-merged) base branch. After any
  stacked-PR chain merges, diff the final branch against `main` to confirm the code actually
  landed, not just that GitHub says "Merged."
- **Return to a clean state after a PR is opened (or its work is otherwise done) —
  don't just stay on that branch.** Check out `main` and pull latest before starting the
  next unrelated task. Otherwise unrelated work quietly piles up on a branch that's already
  tied to an open PR (or one that's since merged), and it becomes unclear which PR a given
  change actually belongs to. If you're not sure a branch's PR has merged yet, check before
  assuming it's safe to keep building on it.

## Definition of Done (applies to every task)

A task is not complete until:
- [ ] Code is pushed to a branch (not `main`)
- [ ] A PR is opened
- [ ] At least one teammate has reviewed the PR
- [ ] No console errors / unhandled exceptions
- [ ] Deploys successfully (Vercel preview for frontend, Railway for backend)
- [ ] Merged to `main`

## AI model tracking

`docs/tracking/ai-model-log.md` tracks who was working, with which AI tool/model, and when — not
Claude-only, since Jeff or Richard may use a different tool (or none). This section only
governs Claude Code sessions; it can't make other tools do the same, since they don't read
this file.

- At the start of every work session, check the most recent entry. If the model you're
  running as differs from that entry, tell the user explicitly (e.g. "model changed from
  Sonnet 5 to X since the last session") and append a new row.
- Also append a new row (even if the model is unchanged) at the start of any session that
  does non-trivial code generation, so the log stays a useful timeline of "when was what
  written," not just "when did the model change." Fill in the Tool column as "Claude Code."
- For the User column: use the name matching this clone's `git config user.email` (see
  Git identity below) — e.g. `alan@aiaction.ai` -> "Alan." If that's ambiguous or unset,
  ask rather than guess.
- Append-only — never edit or delete past entries, so the log stays an honest record.

## Git identity & Vercel deploys

- Set `git config user.email` per-clone to the email verified on the GitHub account that
  owns this repo/Vercel project (currently `alan@aiaction.ai`). Commit *authorship* (the
  email baked into each commit) is separate from *push credentials* — you can push
  successfully while still authoring commits under the wrong account, and GitHub/Vercel
  key off authorship, not who authenticated.
- This repo is intentionally **public**, not private. Reason: Vercel's Hobby plan blocks
  deployments (previews and production alike) whenever a commit or merge's author isn't
  the account that owns the Vercel project — on a private repo this hits *every*
  teammate's commits and merges, not just direct pushes from non-owners. Going public
  removed that restriction.
  - If the repo ever goes private again (e.g. once it holds anything sensitive), expect
    this deployment block to come back for Jeff's and Richard's commits/merges unless the
    team is also on Vercel Pro ($20/seat/mo) by then.

## Secrets

- Never commit `.env` or `.env.local` — both are already in `.gitignore`.
- Never print, log, or paste real values from `backend/.env` (Supabase service_role key,
  MyScript keys) into chat, commit messages, or PR descriptions.
- Use `.env.example` as the template for required variable names only.
- **The repo is public** — treat that as the real enforced boundary, not `.gitignore`
  alone. Nothing committed here can ever be assumed private, even briefly.

## Local dev environment

- Prerequisites: Python 3.11+, Node.js 18.17+.
- `.env` values (Supabase, MyScript) come from Alan via a safe channel (password manager
  or similar) — never generate, guess, or fabricate these. If they're missing, ask the
  user rather than inventing placeholder-looking real values.
- `frontend/.env.local`'s `NEXT_PUBLIC_BACKEND_API_URL` is a real decision, not a fixed
  default: `http://localhost:8000` if the backend is also running locally, or
  `https://math-tutor-mvp-production.up.railway.app` (live) if not. Don't silently assume
  one — ask which the user wants if it's not already set.
- `run-dev.ps1` (repo root, Windows) starts both dev servers in separate windows with one
  command — use it instead of writing new start scripts.
- Full manual setup steps are in `README.md` — read that before improvising an install
  process.

## Working style — decisions and multi-issue fixes

- **Tradeoffs get prose, not forced-choice prompts.** When a decision is a genuine
  tradeoff (design, cost, product/UX — "should we do A or B and why") rather than a quick
  mechanical pick (which library, which file), lay it out as plain text with a clear
  recommendation and reasoning, and let the conversation continue naturally. Reserve
  structured multiple-choice prompts for narrow, mechanical choices where a quick forced
  pick is genuinely what's needed.
- **Fix one problem at a time.** If an audit or investigation turns up more than one
  issue, don't bundle fixes for all of them into a single change. Check which problem,
  and which solution approach, the user wants to tackle before starting each one.
- **Copy approved plans into the project before implementing.** Claude Code's plan mode
  writes to one auto-managed file outside the repo, and that same file gets overwritten the
  next time an unrelated plan is started — so anything meant to survive across sessions
  needs a copy. Once a plan is approved, save it to `.claude/plans/<descriptive-name>.md`
  in the repo (already gitignored — local to this machine, not shared with the team) using
  a name tied to the ticket/task, not the tool's randomly-generated one, before starting
  implementation.
- **Open every plan with "What this unlocks."** Before the Context section, state in 2-4
  sentences what becomes possible once the plan is done — start from the ticket's own story
  one-liner and expand it concretely (what can now be built on top of this, what's still
  not user-visible yet, what it directly unblocks). AC bullets say what's true when it's
  done; this says why that's worth doing. Applies to every plan, not just ticket-specific
  ones.
- **Re-check live state right before reporting it — don't recite it from memory.** PR/merge
  status, branch state, and similar facts change during a session and can go stale between
  one message and the next, since the user or a teammate can change them outside the
  conversation entirely. Before telling the user something is open, merged, blocked, or
  still needs doing, run one fresh check (`gh pr list`, `git log`, etc.) right before saying
  it, instead of repeating an earlier snapshot from the conversation. This is a single check
  gated on the moment of making that claim — not a repeated or proactive poll, and it
  doesn't apply to things done earlier in the same turn (a file just written, a commit just
  made isn't "stale"). Got this wrong once this session — reported a PR as still open
  several turns after it had actually merged.

## Test Pyramid

Applies as new code is written, not as a one-time backfill effort — see
`docs/tracking/decision-log.md`'s "Test pyramid design + CI wiring deferred to 2nd MVP" entry
for the full unit/integration/E2E design (that infrastructure build-out is deferred; this
per-change practice is not):

- **New pure logic → unit test, no mocking.** No I/O, no external system touched by the test.
- **New code touching an external system (DB, API, filesystem, queue) → integration test
  against a real test instance of that system, not a mock of it.**
- **New user-facing flow → ask before adding E2E coverage.** Don't add it automatically.
- **Test via the public interface only — never assert on internal implementation details.**

Currently applies to backend only (already the existing practice — every backend module has
shipped with tests alongside it, e.g. `recognition.py`, `latex_parser.py`, `canonical_form.py`,
`db.py`). Frontend has zero test infrastructure yet, so this waits there until a frontend test
framework is chosen (open question in `.claude/plans/test-pyramid-design.md`) — not decided
here.

## Project structure

```
/frontend           Next.js client
/backend            FastAPI backend
/docs               Finalized/agreed content only
  /architecture     Architecture diagrams, system design docs, API contract
  /tracking         Task board, task tracker, AI model log
  /content          Seed/curriculum content sourced for the problem bank
```

Working drafts, curriculum content, and meeting notes live in the team's shared Google
Drive, not this repo. Only commit content here once it's finalized.

## Current team

- Frontend + Recognition/Parser: Alan
- Backend logic (Evaluator, Misconception Detector, Hint Service, Orchestration): Jeff
- Endpoints, content, curriculum: Richard
- Data/Content/Platform lead: Alan

See `docs/architecture/api_contract_draft_20260728.md` for the agreed data models before touching
`backend/models.py`.
