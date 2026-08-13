"""Integration test for misconception_matching.py (tickets #30, #31) against the
real Supabase project.

Requires real SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY (from backend/.env), same
convention as test_rule_drafting_integration.py. Nothing here calls a paid
third-party API, so nothing is mocked - a real throwaway misconception_rules row
is inserted, matched against, then deleted.
"""
import pytest
from dotenv import load_dotenv

from db import get_client
from latex_parser import parse_math_latex
from misconception_matching import match_misconception

load_dotenv()

RULE_ID = "test_fraction_addition_straight_across_INTEGRATION"


@pytest.fixture
def throwaway_fraction_addition_rule():
    client = get_client()
    client.table("misconception_rules").insert(
        {
            "id": RULE_ID,
            "topic": "fractions",
            "description": "Test fixture - adds numerators and denominators straight across.",
            "matching_rule": {
                "operation": "fraction_addition",
                "error_transform": "add_numerators_and_denominators",
                "check": {"type": "symbolic_equivalence", "wrong_result_template": "(a+c)/(b+d)"},
            },
        }
    ).execute()
    yield RULE_ID
    client.table("misconception_rules").delete().eq("id", RULE_ID).execute()


def test_matches_against_a_real_seeded_rule(throwaway_fraction_addition_rule):
    wrong = parse_math_latex(r"\frac{2}{7}")
    result = match_misconception(r"\frac{1}{3} + \frac{1}{4}", wrong)
    assert result == RULE_ID


def test_no_match_against_real_table_when_answer_is_actually_correct(
    throwaway_fraction_addition_rule,
):
    correct = parse_math_latex(r"\frac{7}{12}")
    result = match_misconception(r"\frac{1}{3} + \frac{1}{4}", correct)
    assert result is None
