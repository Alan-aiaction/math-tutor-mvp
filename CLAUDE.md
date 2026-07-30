# Repo Instructions for Claude

This file is read automatically by Claude Code / Claude Cowork when working in this repo.
Follow these rules for every change, without needing to be asked each time.

## Branch & PR workflow — non-negotiable

- **Never push directly to `main`.** Always create a branch first.
- Branch naming: `feature/short-description` or `fix/short-description`.
- Open a Pull Request for every change, however small.
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
