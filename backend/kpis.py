"""KPI data layer for the 3rd MVP parent dashboard (not the dashboard UI itself).

Five signals, each answering a real question a parent might have:
- accuracy trend over time: is my child getting better?
- practice frequency: are they actually practicing?
- average retries: how much do they struggle before getting something right?
- weak spots by topic: what should they focus on?
- total attempts: how much have they actually done overall? (added alongside the real
  dashboard UI - trivial once the other four existed, same underlying attempts data)

child_id is trusted here, not re-verified - same convention attempts.py's
create_attempt() already uses: the caller (main.py's endpoint) is responsible for
having already checked this child_id belongs to the authenticated parent
(children.get_child()) before calling any of these.

Fetches raw rows via the Supabase client and aggregates in Python, matching this
codebase's existing convention (shadow_log_review.py's get_wrong_answer_clusters())
rather than introducing a new querying style for this one module.
"""
from datetime import datetime, timedelta, timezone

from db import get_client


def _fetch_attempts_with_steps(client, child_id: int) -> list[dict]:
    attempts = (
        client.table("attempts").select("id, problem_id, created_at").eq("child_id", child_id).execute().data
    )
    if not attempts:
        return []

    attempt_ids = [a["id"] for a in attempts]
    steps = (
        client.table("attempt_steps")
        .select("attempt_id, is_correct, previous_wrong_count")
        .in_("attempt_id", attempt_ids)
        .execute()
        .data
    )
    steps_by_attempt: dict[int, list[dict]] = {}
    for step in steps:
        steps_by_attempt.setdefault(step["attempt_id"], []).append(step)

    for attempt in attempts:
        attempt["steps"] = steps_by_attempt.get(attempt["id"], [])
    return attempts


def get_accuracy_trend(child_id: int) -> list[dict]:
    """Accuracy per day this child has practiced, oldest first. Empty list if no
    attempts yet - a real, expected state for a brand-new child account."""
    client = get_client()
    attempts = _fetch_attempts_with_steps(client, child_id)

    results_by_date: dict[str, list[bool]] = {}
    for attempt in attempts:
        date = attempt["created_at"][:10]  # ISO timestamp -> "YYYY-MM-DD"
        for step in attempt["steps"]:
            results_by_date.setdefault(date, []).append(step["is_correct"])

    return [
        {"date": date, "accuracy": sum(results) / len(results)}
        for date, results in sorted(results_by_date.items())
    ]


def get_practice_frequency(child_id: int, days: int = 30) -> int:
    """Distinct days this child has practiced in the last `days` days."""
    client = get_client()
    rows = client.table("attempts").select("created_at").eq("child_id", child_id).execute().data
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    dates = set()
    for row in rows:
        created = datetime.fromisoformat(row["created_at"])
        if created >= cutoff:
            dates.add(created.date().isoformat())
    return len(dates)


def get_average_retries(child_id: int) -> float:
    """Mean previous_wrong_count across every step this child has ever submitted -
    0.0 (not an error) when there's no data yet."""
    client = get_client()
    attempts = client.table("attempts").select("id").eq("child_id", child_id).execute().data
    if not attempts:
        return 0.0

    attempt_ids = [a["id"] for a in attempts]
    steps = (
        client.table("attempt_steps")
        .select("previous_wrong_count")
        .in_("attempt_id", attempt_ids)
        .execute()
        .data
    )
    if not steps:
        return 0.0
    return sum(step["previous_wrong_count"] for step in steps) / len(steps)


def get_total_attempts(child_id: int) -> int:
    """Total number of attempts this child has ever made - an effort-based "problems
    solved" figure for the dashboard, not a correctness judgment. Trivial by design:
    every attempt row counts, regardless of whether every step in it was correct."""
    client = get_client()
    rows = client.table("attempts").select("id").eq("child_id", child_id).execute().data
    return len(rows)


def get_weak_spots_by_topic(child_id: int) -> list[dict]:
    """Accuracy per problem topic, weakest first - buildable today without any
    timestamp dependency, but grouped with the other three KPIs since it's the same
    data-layer piece of work."""
    client = get_client()
    attempts = _fetch_attempts_with_steps(client, child_id)
    if not attempts:
        return []

    problem_ids = list({a["problem_id"] for a in attempts})
    problems = client.table("problems").select("id, topic").in_("id", problem_ids).execute().data
    topic_by_problem = {p["id"]: p["topic"] for p in problems}

    correct_by_topic: dict[str, int] = {}
    total_by_topic: dict[str, int] = {}
    for attempt in attempts:
        topic = topic_by_problem.get(attempt["problem_id"])
        if topic is None:
            continue
        for step in attempt["steps"]:
            total_by_topic[topic] = total_by_topic.get(topic, 0) + 1
            if step["is_correct"]:
                correct_by_topic[topic] = correct_by_topic.get(topic, 0) + 1

    result = [
        {"topic": topic, "accuracy": correct_by_topic.get(topic, 0) / total}
        for topic, total in total_by_topic.items()
    ]
    result.sort(key=lambda r: r["accuracy"])
    return result
