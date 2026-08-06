"""Integration test for task #13 (AC #2): hits the real, live Supabase project.

Requires real SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY credentials (from backend/.env)
to pass - unlike test_db.py, nothing here is mocked. Kept in its own file so it's
obviously distinct from the always-safe-to-run unit suite. Runs as part of the normal
`pytest` sweep for now since this project has no CI yet; revisit with a pytest marker
if/when CI is added and secrets aren't guaranteed to be present.
"""
from dotenv import load_dotenv

from db import get_client

load_dotenv()


def test_query_against_problems_table_succeeds():
    client = get_client()
    response = client.table("problems").select("*").limit(1).execute()
    assert isinstance(response.data, list)
