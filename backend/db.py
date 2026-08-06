"""Supabase Python client / DB layer (task #13).

Uses the service_role key, not anon: RLS is enabled on every table with zero
policies defined yet (#7), so anon currently has no access to anything, and
service_role is the correct long-term choice for a trusted backend anyway.
"""
import logging
import os

from supabase import Client, create_client

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Raised when the Supabase client can't be created (missing credentials or a
    connection failure), instead of letting the failure crash the caller silently."""


def get_client() -> Client:
    """Create and return a Supabase client using SUPABASE_URL and
    SUPABASE_SERVICE_ROLE_KEY from the environment.

    Raises DatabaseError if credentials are missing or the client can't be created.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        logger.error("Supabase credentials are not configured")
        raise DatabaseError("Supabase credentials are not configured")

    try:
        return create_client(url, key)
    except Exception as exc:
        logger.error("Failed to create Supabase client: %s", exc)
        raise DatabaseError(f"Failed to create Supabase client: {exc}") from exc
