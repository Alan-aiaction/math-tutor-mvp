-- KPI data layer (3rd MVP dashboard prerequisite): neither attempts nor attempt_steps
-- had any timestamp column before this - confirmed directly via information_schema,
-- not assumed - so "accuracy trend over time" and "practice frequency" couldn't be
-- computed at all. attempt_steps.previous_wrong_count persists a value the frontend
-- already computes for hint escalation (ticket #71's wrongTryCounts) but previously
-- discarded at save time - same field name/semantics as CheckStep's existing field
-- for consistency across the stack.
--
-- Both tables are empty (0 rows, confirmed directly) - no backfill needed.

alter table attempts add column created_at timestamptz not null default now();
alter table attempt_steps add column previous_wrong_count integer not null default 0;
