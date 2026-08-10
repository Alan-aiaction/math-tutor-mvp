"""Problem retrieval (task #14, #64)."""
import random

from db import get_client
from models import Problem


class ProblemNotFoundError(Exception):
    """Raised when no problem exists with the given id."""


def get_problem(problem_id: int) -> Problem:
    client = get_client()
    rows = client.table("problems").select("*").eq("id", problem_id).execute().data
    if not rows:
        raise ProblemNotFoundError(f"No problem with id {problem_id}")
    return Problem(**rows[0])


def get_random_problem() -> Problem:
    client = get_client()
    rows = client.table("problems").select("id").execute().data
    if not rows:
        raise ProblemNotFoundError("No problems available")
    problem_id = random.choice(rows)["id"]
    return get_problem(problem_id)
