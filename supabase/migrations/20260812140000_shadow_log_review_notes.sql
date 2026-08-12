-- Task #68 (2nd MVP): tracks which shadow-logged wrong-answer clusters have been
-- reviewed, and the human's plain-language note per cluster - the input ticket #69's
-- LLM-assisted rule-drafting tool consumes. See docs/architecture/shadow-log-review.md.
--
-- Same posture as the other 5 tables (#10): permissive RLS baseline for anon/authenticated
-- (no real identity to scope to yet), service_role bypasses RLS regardless. Grants already
-- cover this table via #10's ALTER DEFAULT PRIVILEGES, so only the RLS policy is new here.

create table shadow_log_review_notes (
    id                     bigint generated always as identity primary key,
    problem_id             bigint not null references problems(id),
    representative_answer  text not null,      -- the wrong answer that identifies this
                                                 -- cluster - see shadow_log_review.py
    status                 text not null default 'reviewed',  -- no fixed value list yet,
                                                 -- same approach attempts.status already uses
    note                   text,               -- human's plain-language description -
                                                 -- feeds ticket #69 directly
    created_at             timestamptz not null default now(),
    reviewed_at            timestamptz not null default now(),
    unique (problem_id, representative_answer)  -- one note per cluster, upsertable
);

create policy "mvp_permissive_all" on public.shadow_log_review_notes
  for all to anon, authenticated using (true) with check (true);
comment on policy "mvp_permissive_all" on public.shadow_log_review_notes is 'TEMPORARY: MVP-permissive baseline, see #51';
