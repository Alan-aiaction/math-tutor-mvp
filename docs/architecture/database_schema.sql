-- Supabase/Postgres schema design for Math Tutor MVP (task #6).
--
-- Direct mapping from docs/architecture/api_contract_draft_20260728.md. This is a design
-- artifact, not a migration — task #7 ("Write SQL migrations") turns this into the actual
-- migration applied against the live Supabase project, and task #10 adds RLS policies
-- separately. Nothing here has been run against a real database yet.
--
-- Placeholder / pending-confirmation fields (see docs/tracking/decision-log.md for full
-- reasoning on each):
--   - problems.difficulty: numeric 1-5, proposed 2026-08-03, sent to team, pending confirmation.
--   - attempts.status: no fixed value list agreed yet at all (open question in the contract) -
--     kept as plain text with no CHECK constraint so schema creation isn't blocked on it.
--   - misconception_rules.matching_rule: structured comparison stored as jsonb, proposed
--     2026-08-03, sent to team, pending confirmation. The exact operation-type vocabulary
--     inside the JSON is task #29's job, not decided here.

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
