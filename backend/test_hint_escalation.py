"""Unit tests for hint_escalation.py (ticket #71). Pure logic, no mocking."""
import pytest

from hint_escalation import should_escalate


@pytest.mark.parametrize(
    "prior_wrong_count,expected",
    [
        (0, False),  # first-ever try at this step - never escalate
        (1, True),  # this check is the 2nd wrong try - escalate
        (2, True),
        (5, True),
    ],
)
def test_should_escalate(prior_wrong_count, expected):
    assert should_escalate(prior_wrong_count) is expected
