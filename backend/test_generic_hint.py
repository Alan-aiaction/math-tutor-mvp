from generic_hint import get_generic_hint


def test_returns_non_empty_string():
    hint = get_generic_hint()
    assert isinstance(hint, str)
    assert hint.strip() != ""


def test_is_deterministic():
    assert get_generic_hint() == get_generic_hint()
