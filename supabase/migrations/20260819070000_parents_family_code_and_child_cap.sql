-- Independent child login + per-parent child cap (plan:
-- independent-child-login-and-child-cap.md, PR 1 of 3).
--
-- New `parents` table: one row per parent, created lazily (backend/parents.py) rather
-- than at sign-up time, so a parent who signed up before this ships isn't left in a
-- broken state. Holds the two things Supabase Auth's `auth.users` row has no place for:
-- a short human-friendly family_code a child will use to log in independently (PR 2),
-- and a per-parent cap on how many children they can create (fixed default until a
-- real billing system exists to vary it per plan - deferred to 4th MVP, see
-- decision-log.md).

create table parents (
    id             uuid primary key references auth.users(id) on delete cascade,
    family_code    text not null unique,
    max_children   integer not null default 3,
    created_at     timestamptz not null default now()
);

alter table parents enable row level security;

-- Same defense-in-depth caveat as children's own RLS policy: the backend always uses
-- the service_role key and bypasses RLS entirely - this only protects against a
-- hypothetical direct client REST call using the anon key.
create policy "parent_owns_self" on public.parents
  for all to authenticated
  using (id = auth.uid())
  with check (id = auth.uid());
comment on policy "parent_owns_self" on public.parents is 'A parent can only see/modify their own profile row.';
