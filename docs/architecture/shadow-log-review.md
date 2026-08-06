# Reviewing shadow-logged wrong answers (task #63)

## What this is

Every wrong step a student submits already gets saved (`attempt_steps.is_correct = false`,
via task #15) — no extra work needed to capture it. This doc is about *reading* that data,
not storing it.

## Why it exists

2nd MVP's misconception-matching engine (#30) needs real rules built from real groep 7-8
usage data, not guesswork under 1st MVP's time pressure. This view is the raw material for
that — a place to actually look at what students got wrong, and why, once there's real
pilot data to look at.

## How to access it

A Supabase view, `shadow_log_wrong_answers`, joins each wrong `attempt_step` with the
question and correct answer it was actually attempting:

```sql
select * from shadow_log_wrong_answers;
```

Run that either:
- In Supabase's **SQL Editor** (project dashboard → SQL Editor), or
- Via the **Table Editor** — views show up there too, browsable like a regular table.

Each row has: `attempt_step_id`, `student_answer` (what the student wrote), `attempt_id`,
`student_id`, `problem_id`, `question_text`, `correct_answer`.

No new access control — this reads from the same tables the backend already uses, gated by
the same RLS/`service_role` setup (#10). If you don't already have Supabase project access,
that's the same access you'd need for anything else in the database.
