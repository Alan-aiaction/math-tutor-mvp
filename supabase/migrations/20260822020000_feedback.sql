-- Feedback page (plan: feedback-page.md). One shared table for both a parent's and a
-- child's submissions - child_id is null for a parent submission, set for a child one,
-- distinguished the same way children.py already tells the two apart everywhere else.
--
-- child_id is nullable with ON DELETE SET NULL, not CASCADE: if a child is later
-- removed (the existing hard-delete feature), their past feedback content is still
-- useful to keep - only the FK goes away, not the row.

create table feedback (
    id          bigint generated always as identity primary key,
    parent_id   uuid not null references auth.users(id) on delete cascade,
    child_id    bigint references children(id) on delete set null,
    rating      integer not null check (rating between 1 and 5),
    category    text,
    message     text,
    created_at  timestamptz not null default now()
);

alter table feedback enable row level security;

-- Insert-only, no select policy: no admin UI reads this from the client - Alan reviews
-- submissions directly via the Supabase table editor. Same defense-in-depth caveat as
-- every other table here - the backend always uses the service_role key and bypasses
-- RLS entirely; this only protects against a hypothetical direct anon-key REST call.
create policy "parent_inserts_own_feedback" on public.feedback
  for insert to authenticated
  with check (parent_id = auth.uid());
comment on policy "parent_inserts_own_feedback" on public.feedback is 'A parent (or a child acting under their parent account) can only insert feedback attributed to their own parent_id.';
