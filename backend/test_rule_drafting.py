import json
from unittest.mock import MagicMock, patch

import pytest

from models import Problem
from rule_drafting import RuleDraftError, draft_rule_from_note

VALID_DRAFT = {
    "id": "frac_add_denominators",
    "topic": "fractions",
    "description": "Adds numerators and denominators straight across instead of finding a common denominator",
    "matching_rule": {
        "operation": "fraction_addition",
        "error_transform": "add_numerators_and_denominators",
        "check": {"type": "symbolic_equivalence", "wrong_result_template": "(a+c)/(b+d)"},
    },
}

SAMPLE_PROBLEM = Problem(
    id=5,
    topic="fractions",
    difficulty=2,
    question_text="1/3 + 1/4",
    correct_answer="7/12",
    solving_tip=None,
)


def _mock_client_with_note(note_rows):
    mock_client = MagicMock()
    table_mock = mock_client.table.return_value
    table_mock.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = note_rows
    return mock_client


def test_draft_rule_returns_parsed_json_on_valid_llm_response():
    mock_client = _mock_client_with_note([{"note": "adds straight across", "problem_id": 5, "representative_answer": "2/7"}])

    with patch("rule_drafting.get_client", return_value=mock_client), \
         patch("rule_drafting.get_problem", return_value=SAMPLE_PROBLEM), \
         patch("rule_drafting.generate_text", return_value=json.dumps(VALID_DRAFT)):
        result = draft_rule_from_note(5, "2/7")

    assert result == VALID_DRAFT


def test_draft_rule_writes_draft_and_advances_status():
    mock_client = _mock_client_with_note([{"note": "adds straight across", "problem_id": 5, "representative_answer": "2/7"}])

    with patch("rule_drafting.get_client", return_value=mock_client), \
         patch("rule_drafting.get_problem", return_value=SAMPLE_PROBLEM), \
         patch("rule_drafting.generate_text", return_value=json.dumps(VALID_DRAFT)):
        draft_rule_from_note(5, "2/7")

    update_call = mock_client.table.return_value.update
    update_call.assert_called_once_with({"drafted_rule": VALID_DRAFT, "status": "drafted"})


def test_draft_rule_raises_when_no_review_note_exists():
    mock_client = _mock_client_with_note([])

    with patch("rule_drafting.get_client", return_value=mock_client):
        with pytest.raises(RuleDraftError):
            draft_rule_from_note(5, "2/7")


def test_draft_rule_raises_on_non_json_llm_response():
    mock_client = _mock_client_with_note([{"note": "adds straight across", "problem_id": 5, "representative_answer": "2/7"}])

    with patch("rule_drafting.get_client", return_value=mock_client), \
         patch("rule_drafting.get_problem", return_value=SAMPLE_PROBLEM), \
         patch("rule_drafting.generate_text", return_value="not json at all"):
        with pytest.raises(RuleDraftError):
            draft_rule_from_note(5, "2/7")


def test_draft_rule_raises_on_missing_top_level_key():
    mock_client = _mock_client_with_note([{"note": "adds straight across", "problem_id": 5, "representative_answer": "2/7"}])
    incomplete = {k: v for k, v in VALID_DRAFT.items() if k != "description"}

    with patch("rule_drafting.get_client", return_value=mock_client), \
         patch("rule_drafting.get_problem", return_value=SAMPLE_PROBLEM), \
         patch("rule_drafting.generate_text", return_value=json.dumps(incomplete)):
        with pytest.raises(RuleDraftError):
            draft_rule_from_note(5, "2/7")


def test_draft_rule_raises_on_missing_matching_rule_key():
    mock_client = _mock_client_with_note([{"note": "adds straight across", "problem_id": 5, "representative_answer": "2/7"}])
    bad = dict(VALID_DRAFT)
    bad["matching_rule"] = {"operation": "fraction_addition"}  # missing error_transform, check

    with patch("rule_drafting.get_client", return_value=mock_client), \
         patch("rule_drafting.get_problem", return_value=SAMPLE_PROBLEM), \
         patch("rule_drafting.generate_text", return_value=json.dumps(bad)):
        with pytest.raises(RuleDraftError):
            draft_rule_from_note(5, "2/7")


def test_draft_rule_raises_on_missing_check_key():
    mock_client = _mock_client_with_note([{"note": "adds straight across", "problem_id": 5, "representative_answer": "2/7"}])
    bad = json.loads(json.dumps(VALID_DRAFT))
    del bad["matching_rule"]["check"]["wrong_result_template"]

    with patch("rule_drafting.get_client", return_value=mock_client), \
         patch("rule_drafting.get_problem", return_value=SAMPLE_PROBLEM), \
         patch("rule_drafting.generate_text", return_value=json.dumps(bad)):
        with pytest.raises(RuleDraftError):
            draft_rule_from_note(5, "2/7")
