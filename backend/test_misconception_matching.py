"""Unit tests for misconception_matching.py (tickets #30, #31).

Mocked Supabase client, no real DB - covers: a real match against both worked
examples from the rule-format proposal (fraction_addition, fraction_subtraction),
an explicit no-match returning None (#31's own AC), question_text that isn't
parseable math (word problems), no rules seeded at all, and a rule whose
operation isn't recognized.
"""
from unittest.mock import MagicMock, patch

from latex_parser import parse_math_latex
from misconception_matching import match_misconception

FRACTION_ADDITION_RULE = {
    "id": "fraction_addition_straight_across",
    "topic": "fractions",
    "description": "Adds numerators and denominators straight across instead of finding a common denominator.",
    "matching_rule": {
        "operation": "fraction_addition",
        "error_transform": "add_numerators_and_denominators",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "(a+c)/(b+d)"},
    },
    "escalation_hint_id": None,
}

FRACTION_SUBTRACTION_RULE = {
    "id": "fraction_subtraction_straight_across",
    "topic": "fractions",
    "description": "Subtracts numerators and denominators straight across.",
    "matching_rule": {
        "operation": "fraction_subtraction",
        "error_transform": "subtract_numerators_and_denominators",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "(a-c)/(b-d)"},
    },
    "escalation_hint_id": None,
}


def _mock_client_with_rules(rules):
    mock_client = MagicMock()
    mock_client.table.return_value.select.return_value.execute.return_value.data = rules
    return mock_client


def test_matches_fraction_addition_straight_across_mistake():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([FRACTION_ADDITION_RULE]),
    ):
        wrong = parse_math_latex(r"\frac{2}{7}")  # 1/3 + 1/4 added straight across
        result = match_misconception(r"\frac{1}{3} + \frac{1}{4}", wrong)
    assert result == "fraction_addition_straight_across"


def test_matches_fraction_subtraction_straight_across_mistake():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([FRACTION_SUBTRACTION_RULE]),
    ):
        wrong = parse_math_latex(r"\frac{1}{1}")  # (3-2)/(4-3) for 3/4 - 2/3
        result = match_misconception(r"\frac{3}{4} - \frac{2}{3}", wrong)
    assert result == "fraction_subtraction_straight_across"


def test_no_match_returns_explicit_none_not_exception():
    """Ticket #31's own AC: explicit None, not an empty string or exception."""
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([FRACTION_ADDITION_RULE]),
    ):
        correct = parse_math_latex(r"\frac{7}{12}")  # the actually-correct answer
        result = match_misconception(r"\frac{1}{3} + \frac{1}{4}", correct)
    assert result is None


def test_no_rules_seeded_returns_none():
    with patch("misconception_matching.get_client", return_value=_mock_client_with_rules([])):
        wrong = parse_math_latex(r"\frac{2}{7}")
        result = match_misconception(r"\frac{1}{3} + \frac{1}{4}", wrong)
    assert result is None


def test_unparseable_question_text_returns_none_not_exception():
    """Word problems (or any non-LaTeX question_text) can't have operands
    extracted - must degrade safely to None, not raise."""
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([FRACTION_ADDITION_RULE]),
    ):
        wrong = parse_math_latex(r"\frac{2}{7}")
        result = match_misconception(
            "Julia has a bag with 37 licorice candies. She shares the candies with 7 friends.",
            wrong,
        )
    assert result is None


def test_unrecognized_rule_operation_is_skipped_not_crashed():
    unknown_op_rule = {
        **FRACTION_ADDITION_RULE,
        "matching_rule": {
            **FRACTION_ADDITION_RULE["matching_rule"],
            "operation": "percentage_of_total",
        },
    }
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([unknown_op_rule]),
    ):
        wrong = parse_math_latex(r"\frac{2}{7}")
        result = match_misconception(r"\frac{1}{3} + \frac{1}{4}", wrong)
    assert result is None
