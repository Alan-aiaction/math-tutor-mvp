"""Attempt persistence (task #15).

First real database write in this backend - an attempt (with its steps) gets
saved to Supabase, not just evaluated in memory.
"""
from postgrest.exceptions import APIError

from db import get_client
from models import Attempt, Step


class AttemptPersistenceError(Exception):
    """Raised when an attempt can't be persisted for a data reason (e.g. a
    nonexistent problem_id) - distinct from db.DatabaseError, which means the
    connection itself failed."""


def create_attempt(problem_id: int, child_id: int, status: str, steps: list[dict]) -> Attempt:
    """Persist an attempt and its steps, returning the saved Attempt with
    server-generated IDs.

    child_id (3rd MVP) replaces the old free-text student_id access code - the caller is
    responsible for having already verified this child_id belongs to the authenticated
    parent (see children.get_child) before calling this.

    Inserts the attempt row first, then all steps in one bulk insert - not
    atomic across both tables (supabase-py has no easy multi-table transaction
    without a Postgres RPC), but the steps insert itself is all-or-nothing, so
    "only some steps persisted" can't happen.
    """
    client = get_client()

    try:
        attempt_row = (
            client.table("attempts")
            .insert({"problem_id": problem_id, "child_id": child_id, "status": status})
            .execute()
            .data[0]
        )
    except APIError as exc:
        raise AttemptPersistenceError(f"Could not create attempt: {exc}") from exc

    attempt_id = attempt_row["id"]

    step_rows = []
    if steps:
        try:
            step_rows = (
                client.table("attempt_steps")
                .insert(
                    [
                        {
                            "attempt_id": attempt_id,
                            "recognized_latex": step["recognized_latex"],
                            "is_correct": step["is_correct"],
                        }
                        for step in steps
                    ]
                )
                .execute()
                .data
            )
        except APIError as exc:
            raise AttemptPersistenceError(f"Could not create attempt steps: {exc}") from exc

    return Attempt(
        id=attempt_id,
        problem_id=problem_id,
        child_id=child_id,
        status=status,
        steps=[
            Step(
                id=row["id"],
                attempt_id=attempt_id,
                recognized_latex=row["recognized_latex"],
                is_correct=row["is_correct"],
            )
            for row in step_rows
        ],
    )
