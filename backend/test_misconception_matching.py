"""Unit tests for misconception_matching.py (tickets #30, #31, #9-bootstrap).

Mocked Supabase client, no real DB - covers: a real match against both worked
examples from the rule-format proposal (fraction_addition, fraction_subtraction),
an explicit no-match returning None (#31's own AC), question_text that isn't
parseable math (word problems), no rules seeded at all, a rule whose operation
isn't recognized, and the bootstrap-batch rule types (multiplication_near_round,
money_decimal_multiplication, multiplication_double_near_round) matched against
real seeded problems' actual question_text - including batch 1's double-
compensation exclusion case and batch 2's double-compensation match case.
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


# --- Bootstrap batch (ticket #9): multiplication_near_round, money_decimal_multiplication ---

FORGOT_ADJUSTMENT_RULE = {
    "id": "multiplication_near_round_forgot_adjustment",
    "topic": "multiplication",
    "description": "Rounds the messy factor to a round number and multiplies, but forgets to compensate back.",
    "matching_rule": {
        "operation": "multiplication_near_round",
        "error_transform": "forgot_compensation_adjustment",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c"},
    },
    "escalation_hint_id": None,
}

WRONG_ADJUSTMENT_AMOUNT_RULE = {
    "id": "multiplication_near_round_wrong_adjustment_amount",
    "topic": "multiplication",
    "description": "Compensates by the raw rounding difference instead of that difference times the other factor.",
    "matching_rule": {
        "operation": "multiplication_near_round",
        "error_transform": "compensated_by_raw_diff_not_scaled_diff",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c - d"},
    },
    "escalation_hint_id": None,
}

MONEY_IGNORES_DECIMAL_RULE = {
    "id": "money_multiplication_ignores_decimal_part",
    "topic": "money",
    "description": "Multiplies only the whole-euro part of a decimal amount, drops the cents.",
    "matching_rule": {
        "operation": "money_decimal_multiplication",
        "error_transform": "dropped_decimal_part",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*floor(b)"},
    },
    "escalation_hint_id": None,
}


def test_matches_forgot_adjustment_against_a_real_seeded_problem():
    # Problem id 12: "6 × 199", correct answer 1194
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([FORGOT_ADJUSTMENT_RULE]),
    ):
        wrong = parse_math_latex("1200")
        result = match_misconception("6 × 199", wrong)
    assert result == "multiplication_near_round_forgot_adjustment"


def test_matches_wrong_adjustment_amount_against_a_real_seeded_problem():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([WRONG_ADJUSTMENT_AMOUNT_RULE]),
    ):
        wrong = parse_math_latex("1199")
        result = match_misconception("6 × 199", wrong)
    assert result == "multiplication_near_round_wrong_adjustment_amount"


def test_no_match_for_multiplication_near_round_when_answer_is_actually_correct():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([FORGOT_ADJUSTMENT_RULE, WRONG_ADJUSTMENT_AMOUNT_RULE]),
    ):
        correct = parse_math_latex("1194")
        result = match_misconception("6 × 199", correct)
    assert result is None


def test_double_compensation_problem_correctly_excluded_not_matched():
    """101 x 99: both factors are near-round - the extractor requires exactly
    one, so this must not match, not pick a factor arbitrarily."""
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([FORGOT_ADJUSTMENT_RULE]),
    ):
        wrong = parse_math_latex("9999")  # some wrong answer, doesn't matter which
        result = match_misconception("101 × 99", wrong)
    assert result is None


def test_matches_money_ignores_decimal_against_a_real_seeded_problem():
    # Problem id 33: "3 × €19.50", correct answer 58.50
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([MONEY_IGNORES_DECIMAL_RULE]),
    ):
        wrong = parse_math_latex("57")
        result = match_misconception("3 × €19.50", wrong)
    assert result == "money_multiplication_ignores_decimal_part"


def test_no_match_for_money_rule_when_answer_is_actually_correct():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([MONEY_IGNORES_DECIMAL_RULE]),
    ):
        correct = parse_math_latex("58.50")
        result = match_misconception("3 × €19.50", correct)
    assert result is None


# --- Bootstrap batch 2 (ticket #9): 4 more rules on the same 2 operations, plus
# a new multiplication_double_near_round operation for the double-compensation case ---

WRONG_COMPENSATION_DIRECTION_RULE = {
    "id": "multiplication_near_round_wrong_compensation_direction",
    "topic": "multiplication",
    "description": "Scales the compensation correctly but adds it instead of subtracting it (or vice versa).",
    "matching_rule": {
        "operation": "multiplication_near_round",
        "error_transform": "wrong_compensation_sign",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c + a*d"},
    },
    "escalation_hint_id": None,
}

DOUBLE_FORGOT_BOTH_RULE = {
    "id": "multiplication_double_near_round_forgot_both_adjustments",
    "topic": "multiplication",
    "description": "Rounds both factors to round numbers and multiplies, forgetting both compensations.",
    "matching_rule": {
        "operation": "multiplication_double_near_round",
        "error_transform": "forgot_both_compensation_adjustments",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*c"},
    },
    "escalation_hint_id": None,
}

MONEY_MISPLACED_DECIMAL_RULE = {
    "id": "money_multiplication_misplaced_decimal_point",
    "topic": "money",
    "description": "Multiplies as if the price were whole cents, but doesn't shift the decimal point back.",
    "matching_rule": {
        "operation": "money_decimal_multiplication",
        "error_transform": "misplaced_decimal_point",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*b*100"},
    },
    "escalation_hint_id": None,
}

MONEY_ROUNDS_PRICE_FIRST_RULE = {
    "id": "money_multiplication_rounds_price_before_multiplying",
    "topic": "money",
    "description": "Rounds the price to the nearest euro first, then multiplies, instead of using the exact decimal value.",
    "matching_rule": {
        "operation": "money_decimal_multiplication",
        "error_transform": "rounded_price_before_multiplying",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "a*floor(b + 1/2)"},
    },
    "escalation_hint_id": None,
}


def test_matches_wrong_compensation_direction_against_a_real_seeded_problem():
    # Problem id 12: "6 × 199", correct answer 1194
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([WRONG_COMPENSATION_DIRECTION_RULE]),
    ):
        wrong = parse_math_latex("1206")
        result = match_misconception("6 × 199", wrong)
    assert result == "multiplication_near_round_wrong_compensation_direction"


def test_no_match_for_wrong_compensation_direction_when_answer_is_actually_correct():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([WRONG_COMPENSATION_DIRECTION_RULE]),
    ):
        correct = parse_math_latex("1194")
        result = match_misconception("6 × 199", correct)
    assert result is None


def test_matches_double_compensation_forgot_both_against_a_real_seeded_problem():
    # Problem id 30: "101 × 99", correct answer 9999
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([DOUBLE_FORGOT_BOTH_RULE]),
    ):
        wrong = parse_math_latex("10000")
        result = match_misconception("101 × 99", wrong)
    assert result == "multiplication_double_near_round_forgot_both_adjustments"


def test_matches_double_compensation_forgot_both_against_the_other_seeded_problem():
    # Problem id 31: "99 × 1001", correct answer 99099
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([DOUBLE_FORGOT_BOTH_RULE]),
    ):
        wrong = parse_math_latex("100000")
        result = match_misconception("99 × 1001", wrong)
    assert result == "multiplication_double_near_round_forgot_both_adjustments"


def test_no_match_for_double_compensation_rule_when_answer_is_actually_correct():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([DOUBLE_FORGOT_BOTH_RULE]),
    ):
        correct = parse_math_latex("9999")
        result = match_misconception("101 × 99", correct)
    assert result is None


def test_single_near_round_rules_still_dont_fire_on_double_compensation_problems():
    """Adding the new double-compensation operation must not change the
    existing single-factor extractor's behavior on these 2 problems."""
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([FORGOT_ADJUSTMENT_RULE, WRONG_ADJUSTMENT_AMOUNT_RULE]),
    ):
        wrong = parse_math_latex("10000")
        result = match_misconception("101 × 99", wrong)
    assert result is None


def test_matches_money_misplaced_decimal_against_a_real_seeded_problem():
    # Problem id 33: "3 × €19.50", correct answer 58.50
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([MONEY_MISPLACED_DECIMAL_RULE]),
    ):
        wrong = parse_math_latex("5850")
        result = match_misconception("3 × €19.50", wrong)
    assert result == "money_multiplication_misplaced_decimal_point"


def test_no_match_for_money_misplaced_decimal_when_answer_is_actually_correct():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([MONEY_MISPLACED_DECIMAL_RULE]),
    ):
        correct = parse_math_latex("58.50")
        result = match_misconception("3 × €19.50", correct)
    assert result is None


def test_matches_money_rounds_price_first_against_a_real_seeded_problem():
    # Problem id 33: "3 × €19.50", correct answer 58.50
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([MONEY_ROUNDS_PRICE_FIRST_RULE]),
    ):
        wrong = parse_math_latex("60")
        result = match_misconception("3 × €19.50", wrong)
    assert result == "money_multiplication_rounds_price_before_multiplying"


def test_no_match_for_money_rounds_price_first_when_answer_is_actually_correct():
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules([MONEY_ROUNDS_PRICE_FIRST_RULE]),
    ):
        correct = parse_math_latex("58.50")
        result = match_misconception("3 × €19.50", correct)
    assert result is None


def test_word_problems_still_return_none_with_batch_2_rules_registered():
    """Confirms the 2 seeded word problems (division-with-remainder,
    price-per-kg) still correctly fall through to None - no extractor targets
    them, by design (see module docstring)."""
    with patch(
        "misconception_matching.get_client",
        return_value=_mock_client_with_rules(
            [FORGOT_ADJUSTMENT_RULE, DOUBLE_FORGOT_BOTH_RULE, MONEY_MISPLACED_DECIMAL_RULE]
        ),
    ):
        wrong = parse_math_latex("4")
        result = match_misconception(
            "Julia has a bag with 37 licorice candies. She shares the candies with 7 friends. "
            "Julia and her 7 friends all get the same number of candies. How many candies are left over?",
            wrong,
        )
    assert result is None
