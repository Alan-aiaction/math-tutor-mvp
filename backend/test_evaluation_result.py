from evaluation_result import build_evaluation_result


def test_valid_and_correct_has_no_hint():
    result = build_evaluation_result(is_valid=True, is_correct=True, hint_text="unused")
    assert result.valid is True
    assert result.hint_text is None


def test_valid_and_incorrect_carries_the_given_hint():
    result = build_evaluation_result(is_valid=True, is_correct=False, hint_text="try again")
    assert result.valid is False
    assert result.hint_text == "try again"


def test_invalid_is_always_incorrect_regardless_of_is_correct():
    result = build_evaluation_result(is_valid=False, is_correct=True, hint_text="malformed")
    assert result.valid is False
    assert result.hint_text == "malformed"


def test_misconception_id_defaults_to_none_when_not_given():
    for is_valid, is_correct in [(True, True), (True, False), (False, True), (False, False)]:
        result = build_evaluation_result(is_valid=is_valid, is_correct=is_correct, hint_text="x")
        assert result.misconception_id is None


def test_misconception_id_is_carried_through_when_incorrect():
    result = build_evaluation_result(
        is_valid=True, is_correct=False, hint_text="x", misconception_id="some_rule_id"
    )
    assert result.misconception_id == "some_rule_id"


def test_misconception_id_is_dropped_when_step_is_correct():
    """A correct step never carries a misconception_id, even if one was somehow passed -
    mirrors the existing hint_text=None-on-correct behavior."""
    result = build_evaluation_result(
        is_valid=True, is_correct=True, hint_text="x", misconception_id="some_rule_id"
    )
    assert result.misconception_id is None


def test_hint_level_defaults_to_none_when_not_given():
    result = build_evaluation_result(is_valid=True, is_correct=False, hint_text="x")
    assert result.hint_level is None


def test_hint_level_is_carried_through_when_incorrect():
    result = build_evaluation_result(is_valid=True, is_correct=False, hint_text="x", hint_level=2)
    assert result.hint_level == 2


def test_hint_level_is_dropped_when_step_is_correct():
    """Mirrors hint_text/misconception_id's own None-when-correct behavior."""
    result = build_evaluation_result(is_valid=True, is_correct=True, hint_text="x", hint_level=2)
    assert result.hint_level is None
