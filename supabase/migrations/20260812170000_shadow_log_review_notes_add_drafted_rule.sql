-- Task #69 (2nd MVP): stores the LLM's drafted misconception rule for a reviewed
-- shadow-log cluster, before a human approves it and it gets seeded into
-- misconception_rules. See backend/rule_drafting.py.
--
-- Additive, nullable - no data migration needed, no RLS change (same table, same
-- mvp_permissive_all policy from #68 already covers this column).

alter table shadow_log_review_notes add column drafted_rule jsonb;
