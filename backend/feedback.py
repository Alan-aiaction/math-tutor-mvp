"""Feedback page (plan: feedback-page.md). A single insert, no lookups needed - the
caller (main.py) already knows parent_id/child_id from Requester, matching how every
other per-account write in this codebase is scoped.
"""
from db import get_client
from models import Feedback


def create_feedback(
    parent_id: str,
    child_id: int | None,
    rating: int,
    category: str | None,
    message: str | None,
) -> Feedback:
    client = get_client()
    row = (
        client.table("feedback")
        .insert(
            {
                "parent_id": parent_id,
                "child_id": child_id,
                "rating": rating,
                "category": category,
                "message": message,
            }
        )
        .execute()
        .data[0]
    )
    return Feedback(
        id=row["id"],
        parent_id=row["parent_id"],
        child_id=row["child_id"],
        rating=row["rating"],
        category=row["category"],
        message=row["message"],
        created_at=row["created_at"],
    )
