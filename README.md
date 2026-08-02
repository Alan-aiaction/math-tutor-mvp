# Math Tutor MVP

AI-powered Socratic math tutor for groep 7-8 (HAVO-track) students — part of AIAction's
after-school education products. Pilot goal: help students practice math independently,
diagnosing misconceptions and guiding with hints rather than giving direct answers.

**Status: Trial / experiment.** Prioritize free-tier tooling and minimal cost everywhere
(hosting, database, recognition API) unless a decision explicitly says otherwise.

See `/docs` for the full product spec, architecture diagram, and sprint task board
(`docs/math-tutor-task-board.html`).

## Repo structure

```
/frontend   Next.js client (ink capture, step entry, recognition preview)
/backend    FastAPI backend (recognition, parsing, evaluation, misconception detection, hints)
/docs       Product spec, architecture diagram, schema notes, task board
```

## Prerequisites

- Python 3.11+ (developed/tested on 3.12)
- Node.js 18.17+ (developed/tested on Node 24)
- Git

## Getting your `.env` files

Copy `.env.example` to `backend/.env` and `frontend/.env.local`, then fill in the real
values (Supabase, MyScript keys) — get these from Alan via a safe channel (password
manager or similar), **never** via Slack/email/chat, and never commit the filled-in files
(both are already in `.gitignore`). See `CLAUDE.md`'s Secrets section for the full rules —
this repo is public, so treat `.gitignore` as a convenience, not the real boundary.

`frontend/.env.local` needs one more decision: `NEXT_PUBLIC_BACKEND_API_URL` controls
which backend the frontend's real recognition flow (Draw → Recognise) talks to.
- Point it at `http://localhost:8000` if you're running the backend locally too (see below).
- Point it at `https://math-tutor-mvp-production.up.railway.app` (the live deployed
  backend) if you just want to work on the frontend without running Python locally.

## Local development

### Quick start (Windows)

From the repo root, once your `.env` files are in place:
```
.\run-dev.ps1
```
Starts both the backend and frontend dev servers, each in its own window (so logs stay
visible and either can be stopped independently with Ctrl+C), and opens
`http://localhost:3000` once both are up.

### Manual setup

**Backend:**
```
cd backend
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Run the test suite with `pytest` (from `backend/`, venv active).

**Frontend:**
```
cd frontend
npm install
npm run dev
```
Verify a production build works with `npm run build`.

### Live deployments (no local setup needed, just to look/test)

- Frontend: Vercel (production URL — check the Vercel dashboard, changes on every push to `master`)
- Backend: `https://math-tutor-mvp-production.up.railway.app` — try `/health` for a quick check

## Branch & PR workflow

See `CLAUDE.md` for the full rules (branch naming, PR summaries, the stacked-PR merge-order
trap, Definition of Done). Short version: never push directly to `master`, always open a
PR, get it reviewed before merging.

## Team

- Frontend + Recognition/Parser, Data/Content/Platform lead: Alan
- Backend logic (Evaluator, Misconception Detector, Hint Service, Orchestration): Jeff
- Endpoints, content, curriculum: Richard
