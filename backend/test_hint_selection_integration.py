"""Integration test for hint_selection.py (ticket #33) against the real Supabase project.

Requires real SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY (from backend/.env), same
convention as test_misconception_matching_integration.py. A real throwaway hints
row is inserted, selected against, then deleted.

hints.misconception_id has a real FK to misconception_rules.id, so the throwaway
row must reference a real, permanently-seeded misconception (one of #9's 7 rows)
rather than a made-up id - the fixture only deletes the throwaway hint row, never
touches misconception_rules.
"""
import pytest
from dotenv import load_dotenv

from db import get_client
from generic_hint import get_generic_hint
from hint_selection import select_hint

load_dotenv()

HINT_ID = "test_hint_selection_INTEGRATION"
REAL_SEEDED_MISCONCEPTION_ID = "multiplication_near_round_forgot_adjustment"


@pytest.fixture
def throwaway_hint():
    client = get_client()
    client.table("hints").insert(
        {
            "id": HINT_ID,
            "misconception_id": REAL_SEEDED_MISCONCEPTION_ID,
            "text": "Test fixture hint text.",
            "level": 1,
        }
    ).execute()
    yield REAL_SEEDED_MISCONCEPTION_ID
    client.table("hints").delete().eq("id", HINT_ID).execute()


def test_selects_the_real_seeded_hint(throwaway_hint):
    result = select_hint(throwaway_hint)
    assert result == "Test fixture hint text."


def test_falls_back_to_generic_for_an_unknown_misconception_id():
    result = select_hint("no_such_misconception_id_exists")
    assert result == get_generic_hint()
