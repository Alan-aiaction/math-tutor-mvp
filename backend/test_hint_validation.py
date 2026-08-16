"""Unit tests for hint_validation.py (ticket #72). Pure logic, no mocking, no I/O."""
from hint_validation import MAX_HINT_LENGTH, is_valid_hint


def test_accepts_a_valid_dutch_encouraging_hint():
    assert is_valid_hint("Bijna goed! Denk nog eens goed na over de komma.", "58.50") is True


def test_rejects_empty_text():
    assert is_valid_hint("", "58.50") is False
    assert is_valid_hint("   ", "58.50") is False


def test_rejects_text_over_length_cap():
    too_long = "Bijna goed! " + "a" * MAX_HINT_LENGTH
    assert is_valid_hint(too_long, "58.50") is False


def test_accepts_text_right_at_length_cap():
    exactly_at_cap = "a" * MAX_HINT_LENGTH
    # Not Dutch/encouraging, but this test only cares about the length boundary -
    # use a real Dutch encouraging sentence padded to exactly the cap.
    text = ("Bijna goed! Denk na. " + "x" * MAX_HINT_LENGTH)[:MAX_HINT_LENGTH]
    assert len(text) == MAX_HINT_LENGTH
    assert is_valid_hint(text, "no_such_answer_in_here") is True


def test_rejects_answer_leaking_hint():
    assert is_valid_hint("Bijna goed! Het antwoord is 58.50, denk daar nog eens over na.", "58.50") is False


def test_rejects_non_dutch_hint():
    assert is_valid_hint("Almost there! Think about the decimal point again.", "58.50") is False


def test_rejects_flat_negative_opener():
    assert is_valid_hint("Fout! Dat is niet goed, probeer het opnieuw.", "58.50") is False
    assert is_valid_hint("Nee, dat klopt niet helemaal.", "58.50") is False
    assert is_valid_hint("Verkeerd! Kijk nog eens naar de komma.", "58.50") is False


def test_encouraging_opener_case_insensitive():
    assert is_valid_hint("FOUT! Probeer het nog eens.", "58.50") is False
