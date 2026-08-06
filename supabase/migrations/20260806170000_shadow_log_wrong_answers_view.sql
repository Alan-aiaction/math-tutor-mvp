-- Task #63: makes already-captured wrong answers (attempt_steps.is_correct = false)
-- reviewable, feeding 2nd MVP's misconception rule-building from real usage data.
-- No new storage - attempt_steps already captures every wrong step once #15 ships.
-- See docs/architecture/shadow-log-review.md for how to query this.

create view shadow_log_wrong_answers as
select
    attempt_steps.id as attempt_step_id,
    attempt_steps.recognized_latex as student_answer,
    attempts.id as attempt_id,
    attempts.student_id,
    problems.id as problem_id,
    problems.question_text,
    problems.correct_answer
from attempt_steps
join attempts on attempt_steps.attempt_id = attempts.id
join problems on attempts.problem_id = problems.id
where attempt_steps.is_correct = false;
