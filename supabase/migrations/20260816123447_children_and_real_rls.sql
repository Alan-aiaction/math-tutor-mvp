-- 3rd MVP: parent + child authentication.
--
-- New `children` table: one row per child, owned by a real Supabase Auth parent
-- (auth.users.id). Password is bcrypt-hashed application-side (backend/children.py) -
-- this table never stores a plaintext password.
--
-- Also resolves ticket #51 ("Tighten RLS with real access-code policies... needs #50")
-- for the tables this ticket touches: #50's old plain-text access code never shipped a
-- real identity to scope RLS to, so `attempts`/`attempt_steps` have carried the
-- "mvp_permissive_all" baseline (#10) - any authenticated session, not just the owner,
-- could read/write any row via a direct Supabase REST call. That was an acceptable gap
-- with zero real users; it stops being acceptable the moment real parent accounts with
-- real Supabase Auth sessions exist, which this ticket introduces for the first time.
-- Backend API calls are unaffected either way (backend/db.py always uses the
-- service_role key, which bypasses RLS entirely) - this only closes the direct-REST-call
-- path. `problems`/`misconception_rules`/`hints` keep the permissive baseline: they hold
-- shared content, not per-user data, so there's nothing to scope per-parent.

create table children (
    id             bigint generated always as identity primary key,
    parent_id      uuid not null references auth.users(id) on delete cascade,
    nickname       text not null,
    password_hash  text not null,
    created_at     timestamptz not null default now(),
    unique (parent_id, nickname)  -- unique per parent, not globally - two different
                                   -- parents can each have a child nicknamed "Sam"
);

create policy "parent_owns_children" on public.children
  for all to authenticated
  using (parent_id = auth.uid())
  with check (parent_id = auth.uid());
comment on policy "parent_owns_children" on public.children is 'A parent can only see/modify their own children rows.';

-- #63's shadow_log_wrong_answers view (backend/shadow_log_review.py) passes student_id
-- through but never actually reads it downstream (checked - no reference in that file) -
-- drop and recreate against child_id so the view stays a faithful passthrough of
-- attempts' real current schema, not because anything consumes the column today.
drop view shadow_log_wrong_answers;

-- attempts: student_id (free-text) -> child_id (real FK). No real pilot data exists yet
-- (confirmed earlier this project: the only rows ever in these tables were Alan/Jeff's
-- own dev/test residue, already cleared once before) - clean cutover, nothing to migrate.
delete from attempt_steps;
delete from attempts;

alter table attempts drop column student_id;
alter table attempts add column child_id bigint not null references children(id);

create view shadow_log_wrong_answers as
select
    attempt_steps.id as attempt_step_id,
    attempt_steps.recognized_latex as student_answer,
    attempts.id as attempt_id,
    attempts.child_id,
    problems.id as problem_id,
    problems.question_text,
    problems.correct_answer
from attempt_steps
join attempts on attempt_steps.attempt_id = attempts.id
join problems on attempts.problem_id = problems.id
where attempt_steps.is_correct = false;

drop policy "mvp_permissive_all" on public.attempts;
create policy "parent_owns_attempts" on public.attempts
  for all to authenticated
  using (exists (select 1 from children c where c.id = attempts.child_id and c.parent_id = auth.uid()))
  with check (exists (select 1 from children c where c.id = attempts.child_id and c.parent_id = auth.uid()));
comment on policy "parent_owns_attempts" on public.attempts is 'A parent can only see/modify attempts belonging to one of their own children.';

drop policy "mvp_permissive_all" on public.attempt_steps;
create policy "parent_owns_attempt_steps" on public.attempt_steps
  for all to authenticated
  using (exists (
    select 1 from attempts a join children c on c.id = a.child_id
    where a.id = attempt_steps.attempt_id and c.parent_id = auth.uid()
  ))
  with check (exists (
    select 1 from attempts a join children c on c.id = a.child_id
    where a.id = attempt_steps.attempt_id and c.parent_id = auth.uid()
  ));
comment on policy "parent_owns_attempt_steps" on public.attempt_steps is 'A parent can only see/modify steps belonging to their own children''s attempts.';
