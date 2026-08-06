# AI Tool/Model Log

Tracks who was working, with which AI tool and model, and when — for provenance and
auditing. Not Claude-specific: Jeff/Richard may use a different AI tool (Copilot, Cursor,
ChatGPT, etc.) or none at all — log whatever's actually true.

Replaces `docs/tracking/ai-model-log.md`'s old shared table (now frozen, see that file for
the pre-2026-08-06 history) — every PR editing the same table meant any two PRs open at once
reliably conflicted. Here, **one file per work session** instead: two new files can never
collide, so this removes the conflict source entirely, the same reasoning already used for
`supabase/migrations/`.

## Convention

- One new file per work session, named `YYYYMMDDHHMM-user-short-slug.md` (e.g.
  `202608061430-alan-evaluator-pipeline.md`) — sortable by filename, so the folder reads
  chronologically.
- Never edit or delete a past session's file — same append-only spirit as before, just
  enforced structurally (a new file per entry) instead of by convention alone.
- Each file's content:
  ```markdown
  # YYYY-MM-DD — User — Tool

  - **Model:** Model Name (`model-id`)
  - **Notes:** Session covering: ...
  ```

**For Claude Code sessions specifically**: maintained automatically per the instructions in
`CLAUDE.md`. **For any other tool** (or no AI): please add a file by hand for a substantial
chunk of AI-assisted work, or note "Human, no AI" if that's what happened — your tool won't
know this convention exists otherwise.
