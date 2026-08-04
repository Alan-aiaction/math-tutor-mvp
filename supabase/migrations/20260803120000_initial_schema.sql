-- Initial schema migration for Math Tutor MVP (task #7).
--
-- Applied against the live Supabase project on 2026-08-03 via the Supabase MCP server's
-- apply_migration tool, and verified: all 5 tables exist with the expected columns/types,
-- and the attempts.problem_id -> problems.id foreign key was manually tested (a valid
-- insert succeeded, an insert referencing a nonexistent problem_id was correctly rejected
-- with a foreign key violation) before the test rows were cleaned up.
--
-- Source design: docs/architecture/database_schema.sql (task #6). Kept identical here -
-- see that file's header comment for the placeholder/pending-confirmation fields
-- (difficulty scale, matching_rule format) and docs/tracking/decision-log.md for reasoning.
--
-- Note: Supabase enables Row Level Security on new tables by default. All 5 tables now
-- have RLS enabled with zero policies defined yet, meaning only the service_role key can
-- currently read/write them - relevant starting point for task #10, not a gap in this one.

create table problems (
    id              bigint generated always as identity primary key,
    topic           text not null,
    difficulty      integer not null,       -- 1-5, see decision log
    question_text   text not null,
    correct_answer  text not null,
    solving_tip     text                    -- nullable; per-problem worked-strategy hint,
                                             -- shown regardless of the student's answer
);

create table attempts (
    id          bigint generated always as identity primary key,
    problem_id  bigint not null references problems(id),
    student_id  text not null,
    status      text not null               -- no fixed value list agreed yet, see decision log
);

create table attempt_steps (
    id               bigint generated always as identity primary key,
    attempt_id       bigint not null references attempts(id),
    recognized_latex text not null,
    is_correct       boolean not null
);

-- id is text (not bigint) here and on hints - both are content authored by Richard/Jeff
-- with human-readable slug ids (e.g. 'frac_add_denominators'), not app-generated rows.
create table misconception_rules (
    id                 text primary key,
    topic              text not null,
    description        text not null,
    matching_rule      jsonb not null,      -- structured comparison, see decision log
    escalation_hint_id text                 -- nullable; deliberately NOT a foreign key -
                                             -- enforcing both directions between this table
                                             -- and hints creates an insert-order cycle for
                                             -- no real benefit at seed-data scale (#9)
);

create table hints (
    id                text primary key,
    misconception_id  text not null references misconception_rules(id),
    text              text not null,
    level             integer not null      -- 1 = first hint, 2 = escalated/more direct
);
