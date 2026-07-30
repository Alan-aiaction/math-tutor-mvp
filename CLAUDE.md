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

## Definition of Done (applies to every task)

A task is not complete until:
- [ ] Code is pushed to a branch (not `main`)
- [ ] A PR is opened
- [ ] At least one teammate has reviewed the PR
- [ ] No console errors / unhandled exceptions
- [ ] Deploys successfully (Vercel preview for frontend, Railway for backend)
- [ ] Merged to `main`

## Secrets

- Never commit `.env` or `.env.local` — both are already in `.gitignore`.
- Never print, log, or paste real values from `backend/.env` (Supabase service_role key,
  MyScript keys) into chat, commit messages, or PR descriptions.
- Use `.env.example` as the template for required variable names only.

## Project structure

```
/frontend   Next.js client
/backend    FastAPI backend
/docs       Specs, architecture, API contract — finalized/agreed content only
```

Working drafts, curriculum content, and meeting notes live in the team's shared Google
Drive, not this repo. Only commit content here once it's finalized.

## Current team

- Frontend + Recognition/Parser: Alan
- Backend logic (Evaluator, Misconception Detector, Hint Service, Orchestration): Jeff
- Endpoints, content, curriculum: Richard
- Data/Content/Platform lead: Alan

See `docs/api_contract_draft_20260728.md` for the agreed data models before touching
`backend/models.py`.
