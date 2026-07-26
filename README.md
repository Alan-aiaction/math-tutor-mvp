# Math Tutor MVP

AI-powered Socratic math tutor for groep 7-8 (HAVO-track) students — part of AIAction's
after-school education products. Pilot goal: help students practice math independently,
diagnosing misconceptions and guiding with hints rather than giving direct answers.

**Status: Trial / experiment.** Prioritize free-tier tooling and minimal cost everywhere
(hosting, database, recognition API) unless a decision explicitly says otherwise.

See `/docs` for the full product spec and architecture diagram.

## Repo structure

```
/frontend   Next.js client (ink capture, step entry, recognition preview)
/backend    FastAPI backend (recognition, parsing, evaluation, misconception detection, hints)
/docs       Product spec, architecture diagram, schema notes
```

## Local development

### Frontend
```
cd frontend
npm install
npm run dev
```

### Backend
```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Copy `.env.example` to `.env` (backend) / `.env.local` (frontend) and fill in your own
copies of the shared keys (Supabase, MyScript) — get these from whoever set up the
project, never commit real values.

## Branch discipline (no enforced protection on GitHub Free)

GitHub's free tier doesn't enforce branch protection on private repos, so we're doing
this by agreement instead:

- Never push directly to `main`.
- Always open a PR, even for small changes.
- At least one other team member should glance at the diff before merging.
- Keep PRs small and scoped — easier to review, easier to revert if something breaks.

## Team

- Frontend: [Dev A]
- Backend / math engine: [Dev B]
- Data, content & platform: [Dev C / lead]
