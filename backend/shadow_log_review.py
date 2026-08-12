"""Shadow-log review workflow (ticket #68, 2nd MVP).

Turns the raw shadow_log_wrong_answers view (task #63) into reviewable, repeated-pattern
clusters instead of a wall of individual rows - and tracks which clusters have already
been reviewed, so review()'s output (a plain-language note) is real input for ticket #69's
drafting tool, not just raw data.

Reuses the existing, tested canonical-form comparison logic (latex_parser.py,
canonical_form.py) already built for comparing a student's answer to a correct answer -
the same "are these mathematically the same, regardless of exact text" check is exactly
what's needed to group wrong answers into real patterns.
"""
from canonical_form import are_equivalent
from db import get_client
from latex_parser import LatexParseError, parse_math_latex


def _fetch_unreviewed_rows(client, problem_id: int | None):
    query = client.table("shadow_log_wrong_answers").select("*")
    if problem_id is not None:
        query = query.eq("problem_id", problem_id)
    rows = query.execute().data

    reviewed_query = client.table("shadow_log_review_notes").select("problem_id, representative_answer")
    if problem_id is not None:
        reviewed_query = reviewed_query.eq("problem_id", problem_id)
    reviewed = {
        (r["problem_id"], r["representative_answer"]) for r in reviewed_query.execute().data
    }
    return rows, reviewed


def get_wrong_answer_clusters(problem_id: int | None = None) -> list[dict]:
    """Group shadow-logged wrong answers into reviewable clusters.

    Rows are grouped by mathematical equivalence (not exact string match) within each
    problem, so e.g. "2/7" and "2 / 7" land in the same cluster. Rows whose student_answer
    fails to parse land in their own parse_failed cluster per problem, rather than being
    dropped or crashing - a real, distinct signal (recognition issue, not a misconception).
    Clusters already marked reviewed (shadow_log_review_notes) are excluded. Sorted by
    occurrence_count descending - the most-repeated mistake is the most actionable one.
    """
    client = get_client()
    rows, reviewed = _fetch_unreviewed_rows(client, problem_id)

    by_problem: dict[int, list[dict]] = {}
    for row in rows:
        by_problem.setdefault(row["problem_id"], []).append(row)

    clusters: list[dict] = []
    for pid, problem_rows in by_problem.items():
        question_text = problem_rows[0]["question_text"]
        correct_answer = problem_rows[0]["correct_answer"]

        parsed: list[tuple[dict, object]] = []
        parse_failed_rows: list[dict] = []
        for row in problem_rows:
            try:
                parsed.append((row, parse_math_latex(row["student_answer"])))
            except LatexParseError:
                parse_failed_rows.append(row)

        # Group parsed rows by canonical equivalence - not exact string match.
        groups: list[list[tuple[dict, object]]] = []
        for row, expr in parsed:
            placed = False
            for group in groups:
                if are_equivalent(expr, group[0][1]):
                    group.append((row, expr))
                    placed = True
                    break
            if not placed:
                groups.append([(row, expr)])

        for group in groups:
            representative_answer = group[0][0]["student_answer"]
            if (pid, representative_answer) in reviewed:
                continue
            clusters.append({
                "problem_id": pid,
                "question_text": question_text,
                "correct_answer": correct_answer,
                "representative_answer": representative_answer,
                "occurrence_count": len(group),
                "attempt_step_ids": [r["attempt_step_id"] for r, _ in group],
                "parse_failed": False,
            })

        if parse_failed_rows:
            representative_answer = parse_failed_rows[0]["student_answer"]
            if (pid, representative_answer) not in reviewed:
                clusters.append({
                    "problem_id": pid,
                    "question_text": question_text,
                    "correct_answer": correct_answer,
                    "representative_answer": representative_answer,
                    "occurrence_count": len(parse_failed_rows),
                    "attempt_step_ids": [r["attempt_step_id"] for r in parse_failed_rows],
                    "parse_failed": True,
                })

    clusters.sort(key=lambda c: c["occurrence_count"], reverse=True)
    return clusters


def record_review(problem_id: int, representative_answer: str, note: str, status: str = "reviewed") -> None:
    """Record a human's review of a wrong-answer cluster.

    `note` is the plain-language description of the pattern - this is the input ticket
    #69's LLM-assisted rule-drafting tool consumes. Upserts on (problem_id,
    representative_answer) so re-reviewing the same cluster updates it rather than
    duplicating a row.
    """
    client = get_client()
    client.table("shadow_log_review_notes").upsert(
        {
            "problem_id": problem_id,
            "representative_answer": representative_answer,
            "status": status,
            "note": note,
        },
        on_conflict="problem_id,representative_answer",
    ).execute()
