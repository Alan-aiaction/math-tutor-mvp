import os
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from auth import issue_child_token
from children import ChildError
from main import app
from models import Attempt, Child, Parent
from recognition import RecognitionError

# raise_server_exceptions=False: without this, TestClient re-raises the original
# exception for debugging convenience, even though the app's own exception handler
# already produced a response - we need to inspect that actual HTTP response here.
client = TestClient(app, raise_server_exceptions=False)

FAKE_PARENT_ID = "11111111-1111-1111-1111-111111111111"
AUTH_HEADER = {"Authorization": "Bearer fake-token"}


def _mock_parent_auth():
    """Patches main.get_current_parent_id (not auth.get_current_parent_id - main.py
    imports the name directly, so that's where the call is actually looked up) to
    return a fixed parent id without a real Supabase round-trip."""
    return patch("main.get_current_parent_id", return_value=FAKE_PARENT_ID)


def _with_child_session_secret():
    return patch.dict(os.environ, {"CHILD_SESSION_SECRET": "test-secret-at-least-32-bytes-long"})


def _child_auth_header(child_id, parent_id=FAKE_PARENT_ID):
    """A real, verifiable child session token (independent child login, PR 2/3) - not
    mocked, since get_current_child is pure local signature verification with no
    network round-trip to fake out. Must be called from inside a
    _with_child_session_secret() block - and the resulting header used inside that same
    block - since CHILD_SESSION_SECRET has to be set for both issuing and verifying."""
    token = issue_child_token(child_id=child_id, parent_id=parent_id)
    return {"Authorization": f"Bearer {token}"}


# --- CORS (fix #76: Authorization was missing from allow_headers, which silently
# broke every authenticated request from the deployed frontend - see decision log) ---


def test_cors_preflight_allows_authorization_header():
    """Reproduces the exact browser preflight for a cross-origin authenticated request
    (e.g. Vercel frontend -> Railway backend). Before the fix, Authorization was missing
    from allow_headers, so this came back without it - the browser would then block the
    real request and the frontend saw it as a generic network error."""
    response = client.options(
        "/children",
        headers={
            "Origin": "https://math-tutor-mvp.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert "authorization" in allowed_headers
    assert "content-type" in allowed_headers


def test_cors_preflight_allows_delete_method():
    """DELETE /children/{id} (remove-child feature) needs DELETE in allow_methods, the
    same class of gap the Authorization-header fix above closed for allow_headers."""
    response = client.options(
        "/children/1",
        headers={
            "Origin": "https://math-tutor-mvp.vercel.app",
            "Access-Control-Request-Method": "DELETE",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert response.status_code == 200
    assert "DELETE" in response.headers["access-control-allow-methods"]


def test_unhandled_exception_returns_clean_500_not_a_crash():
    # main.capture_exception is mocked here so this unit test doesn't send a real event to
    # the team's live Sentry dashboard on every run (#59) - Sentry delivery itself is a
    # one-time manual check, not something to bake into the permanent suite.
    with (
        patch("main.recognize_math", side_effect=RuntimeError("boom")),
        patch("main.sentry_sdk.capture_exception") as mock_capture,
    ):
        response = client.post(
            "/recognize",
            json={"strokeGroups": [], "width": 100, "height": 100},
        )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    mock_capture.assert_called_once()


def test_recognition_error_still_maps_to_502_not_shadowed_by_global_handler():
    with patch("main.recognize_math", side_effect=RecognitionError("bad creds")):
        response = client.post(
            "/recognize",
            json={"strokeGroups": [], "width": 100, "height": 100},
        )
    assert response.status_code == 502


def test_request_logging_middleware_logs_method_path_status(caplog):
    with caplog.at_level("INFO", logger="main"):
        response = client.get("/health")
    assert response.status_code == 200
    matching = [r for r in caplog.records if "GET" in r.message and "/health" in r.message]
    assert len(matching) == 1
    assert "200" in matching[0].message


def test_check_attempt_correct_step():
    with _mock_parent_auth():
        response = client.post(
            "/attempts/check",
            json={"steps": [{"recognized_latex": "7/12"}], "correct_answer": "7/12"},
            headers=AUTH_HEADER,
        )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["valid"] is True
    assert results[0]["hint_text"] is None


def test_check_attempt_incorrect_step_gets_hint():
    with _mock_parent_auth():
        response = client.post(
            "/attempts/check",
            json={"steps": [{"recognized_latex": "5/7"}], "correct_answer": "7/12"},
            headers=AUTH_HEADER,
        )
    assert response.status_code == 200
    results = response.json()
    assert results[0]["valid"] is False
    assert results[0]["hint_text"]


def test_check_attempt_multiple_steps_returns_one_result_each():
    with _mock_parent_auth():
        response = client.post(
            "/attempts/check",
            json={
                "steps": [{"recognized_latex": "5/7"}, {"recognized_latex": "7/12"}],
                "correct_answer": "7/12",
            },
            headers=AUTH_HEADER,
        )
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_check_attempt_malformed_correct_answer_returns_400():
    with _mock_parent_auth():
        response = client.post(
            "/attempts/check",
            json={"steps": [{"recognized_latex": "7/12"}], "correct_answer": r"\notacommand{x}"},
            headers=AUTH_HEADER,
        )
    assert response.status_code == 400


def test_check_attempt_without_auth_header_returns_401():
    response = client.post(
        "/attempts/check",
        json={"steps": [{"recognized_latex": "7/12"}], "correct_answer": "7/12"},
    )
    assert response.status_code == 401


# --- Parent profile (child cap groundwork) ---


def test_get_parent_profile_requires_auth():
    response = client.get("/parents/me")
    assert response.status_code == 401


def test_get_parent_profile_success():
    with (
        _mock_parent_auth(),
        patch(
            "main.get_or_create_parent",
            return_value=Parent(id=FAKE_PARENT_ID, family_code="AB12CD", max_children=3, created_at="2026-08-19T00:00:00Z"),
        ),
        patch(
            "main.list_children",
            return_value=[Child(id=1, parent_id=FAKE_PARENT_ID, nickname="Sam", created_at="2026-08-16T00:00:00Z")],
        ),
    ):
        response = client.get("/parents/me", headers=AUTH_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body == {"family_code": "AB12CD", "max_children": 3, "children_count": 1}


# --- Children endpoints (3rd MVP auth) ---


def test_create_child_requires_auth():
    response = client.post("/children", json={"nickname": "Sam", "password": "sesame"})
    assert response.status_code == 401


def test_create_child_success():
    with _mock_parent_auth(), patch(
        "main.create_child",
        return_value=Child(id=1, parent_id=FAKE_PARENT_ID, nickname="Sam", created_at="2026-08-16T00:00:00Z"),
    ):
        response = client.post(
            "/children", json={"nickname": "Sam", "password": "sesame"}, headers=AUTH_HEADER
        )
    assert response.status_code == 200
    assert response.json()["nickname"] == "Sam"


def test_create_child_duplicate_nickname_returns_400():
    with _mock_parent_auth(), patch("main.create_child", side_effect=ChildError("nickname already used")):
        response = client.post(
            "/children", json={"nickname": "Sam", "password": "sesame"}, headers=AUTH_HEADER
        )
    assert response.status_code == 400


def test_list_children_requires_auth():
    response = client.get("/children")
    assert response.status_code == 401


def test_list_children_success():
    with _mock_parent_auth(), patch(
        "main.list_children",
        return_value=[Child(id=1, parent_id=FAKE_PARENT_ID, nickname="Sam", created_at="2026-08-16T00:00:00Z")],
    ):
        response = client.get("/children", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_child_login_wrong_password_returns_401():
    with _mock_parent_auth(), patch("main.verify_child_login", return_value=False):
        response = client.post("/children/1/login", json={"password": "wrong"}, headers=AUTH_HEADER)
    assert response.status_code == 401


def test_delete_child_requires_auth():
    response = client.delete("/children/1")
    assert response.status_code == 401


def test_delete_child_rejects_a_child_that_doesnt_belong_to_this_parent():
    with _mock_parent_auth(), patch("main.get_child", return_value=None):
        response = client.delete("/children/999", headers=AUTH_HEADER)
    assert response.status_code == 403


def test_delete_child_success():
    with (
        _mock_parent_auth(),
        patch(
            "main.get_child",
            return_value=Child(id=1, parent_id=FAKE_PARENT_ID, nickname="Sam", created_at="2026-08-16T00:00:00Z"),
        ),
        patch("main.delete_child", return_value=True) as mock_delete,
    ):
        response = client.delete("/children/1", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json() == {"deleted": True}
    mock_delete.assert_called_once_with(FAKE_PARENT_ID, 1)


def test_child_login_success():
    # Retire-active-child: this endpoint now issues a real child session token too
    # (same shape independent login returns), not just the bare Child it used to.
    with (
        _with_child_session_secret(),
        _mock_parent_auth(),
        patch("main.verify_child_login", return_value=True),
        patch(
            "main.get_child",
            return_value=Child(id=1, parent_id=FAKE_PARENT_ID, nickname="Sam", created_at="2026-08-16T00:00:00Z"),
        ),
    ):
        response = client.post("/children/1/login", json={"password": "sesame"}, headers=AUTH_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["child"]["nickname"] == "Sam"
    assert isinstance(body["token"], str) and len(body["token"]) > 0


# --- Independent child login: POST /children/login, no parent session (PR 2 of 3) ---


def test_independent_child_login_requires_no_auth_header_at_all():
    with (
        patch("main.get_parent_by_family_code", return_value=None),
    ):
        response = client.post(
            "/children/login", json={"family_code": "NOTREAL", "nickname": "Sam", "password": "sesame"}
        )
    # No Authorization header sent above - proves this route never gates on one.
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect login"


def test_independent_child_login_success_issues_a_token():
    with (
        _with_child_session_secret(),
        patch("main.get_parent_by_family_code", return_value=Parent(id=FAKE_PARENT_ID, family_code="AB12CD", max_children=3, created_at="2026-08-19T00:00:00Z")),
        patch(
            "main.get_child_by_nickname",
            return_value=Child(id=1, parent_id=FAKE_PARENT_ID, nickname="Sam", created_at="2026-08-16T00:00:00Z"),
        ),
        patch("main.verify_child_login", return_value=True),
    ):
        response = client.post(
            "/children/login", json={"family_code": "AB12CD", "nickname": "Sam", "password": "sesame"}
        )
    assert response.status_code == 200
    body = response.json()
    assert body["child"]["nickname"] == "Sam"
    assert isinstance(body["token"], str) and len(body["token"]) > 0


def test_independent_child_login_wrong_family_code_returns_generic_401():
    with patch("main.get_parent_by_family_code", return_value=None):
        response = client.post(
            "/children/login", json={"family_code": "WRONGCODE", "nickname": "Sam", "password": "sesame"}
        )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect login"


def test_independent_child_login_wrong_nickname_returns_the_same_generic_401():
    with (
        patch("main.get_parent_by_family_code", return_value=Parent(id=FAKE_PARENT_ID, family_code="AB12CD", max_children=3, created_at="2026-08-19T00:00:00Z")),
        patch("main.get_child_by_nickname", return_value=None),
    ):
        response = client.post(
            "/children/login", json={"family_code": "AB12CD", "nickname": "NotReal", "password": "sesame"}
        )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect login"


def test_independent_child_login_wrong_password_returns_the_same_generic_401():
    with (
        patch("main.get_parent_by_family_code", return_value=Parent(id=FAKE_PARENT_ID, family_code="AB12CD", max_children=3, created_at="2026-08-19T00:00:00Z")),
        patch(
            "main.get_child_by_nickname",
            return_value=Child(id=1, parent_id=FAKE_PARENT_ID, nickname="Sam", created_at="2026-08-16T00:00:00Z"),
        ),
        patch("main.verify_child_login", return_value=False),
    ):
        response = client.post(
            "/children/login", json={"family_code": "AB12CD", "nickname": "Sam", "password": "wrong"}
        )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect login"


# --- require_requester: an independent child's own token on the practice endpoints ---


def test_check_attempt_accepts_a_child_session_token_not_just_a_parent_token():
    with _with_child_session_secret():
        response = client.post(
            "/attempts/check",
            json={"steps": [{"recognized_latex": "7/12"}], "correct_answer": "7/12"},
            headers=_child_auth_header(child_id=1),
        )
    assert response.status_code == 200


def test_create_attempt_accepts_a_child_session_token_for_that_childs_own_id():
    fake_attempt = Attempt(id=1, problem_id=1, child_id=1, steps=[], status="completed", created_at="2026-08-19T00:00:00Z")
    with _with_child_session_secret(), patch("main.create_attempt", return_value=fake_attempt) as mock_create:
        response = client.post(
            "/attempts",
            json={"problem_id": 1, "child_id": 1, "status": "completed", "steps": []},
            headers=_child_auth_header(child_id=1),
        )
    assert response.status_code == 200
    mock_create.assert_called_once()


def test_create_attempt_rejects_a_child_token_used_for_a_different_childs_id():
    with _with_child_session_secret():
        response = client.post(
            "/attempts",
            json={"problem_id": 1, "child_id": 999, "status": "completed", "steps": []},
            headers=_child_auth_header(child_id=1),  # token proves child 1, payload claims child 999
        )
    assert response.status_code == 403


# --- Attempts endpoint ownership check (3rd MVP auth) ---


def test_create_attempt_requires_auth():
    response = client.post(
        "/attempts",
        json={"problem_id": 1, "child_id": 1, "status": "completed", "steps": []},
    )
    assert response.status_code == 401


def test_create_attempt_rejects_a_child_that_doesnt_belong_to_this_parent():
    with _mock_parent_auth(), patch("main.get_child", return_value=None):
        response = client.post(
            "/attempts",
            json={"problem_id": 1, "child_id": 999, "status": "completed", "steps": []},
            headers=AUTH_HEADER,
        )
    assert response.status_code == 403


# --- Child KPIs endpoint (KPI data layer) ---


def test_get_child_kpis_requires_auth():
    response = client.get("/children/1/kpis")
    assert response.status_code == 401


def test_get_child_kpis_rejects_a_child_that_doesnt_belong_to_this_parent():
    with _mock_parent_auth(), patch("main.get_child", return_value=None):
        response = client.get("/children/999/kpis", headers=AUTH_HEADER)
    assert response.status_code == 403


def test_get_child_kpis_success():
    with (
        _mock_parent_auth(),
        patch(
            "main.get_child",
            return_value=Child(id=1, parent_id=FAKE_PARENT_ID, nickname="Sam", created_at="2026-08-16T00:00:00Z"),
        ),
        patch("main.get_accuracy_trend", return_value=[{"date": "2026-08-16", "accuracy": 0.5}]),
        patch("main.get_practice_frequency", return_value=3),
        patch("main.get_average_retries", return_value=1.5),
        patch("main.get_weak_spots_by_topic", return_value=[{"topic": "fractions", "accuracy": 0.5}]),
        patch("main.get_total_attempts", return_value=47),
    ):
        response = client.get("/children/1/kpis", headers=AUTH_HEADER)
    assert response.status_code == 200
    body = response.json()
    assert body["accuracy_trend"] == [{"date": "2026-08-16", "accuracy": 0.5}]
    assert body["practice_frequency_days"] == 3
    assert body["average_retries"] == 1.5
    assert body["weak_spots_by_topic"] == [{"topic": "fractions", "accuracy": 0.5}]
    assert body["total_attempts"] == 47


def test_get_child_kpis_accepts_a_child_session_token_for_their_own_id():
    # A child's own dashboard (own-data-only) needs to fetch their own kpis without
    # any parent session at all - same require_requester pattern /attempts already uses.
    with (
        _with_child_session_secret(),
        patch("main.get_accuracy_trend", return_value=[]),
        patch("main.get_practice_frequency", return_value=0),
        patch("main.get_average_retries", return_value=0.0),
        patch("main.get_weak_spots_by_topic", return_value=[]),
        patch("main.get_total_attempts", return_value=5),
    ):
        response = client.get("/children/1/kpis", headers=_child_auth_header(child_id=1))
    assert response.status_code == 200
    assert response.json()["total_attempts"] == 5


def test_get_child_kpis_rejects_a_child_token_for_a_different_childs_id():
    with _with_child_session_secret():
        response = client.get("/children/999/kpis", headers=_child_auth_header(child_id=1))
    assert response.status_code == 403


# --- question_text / misconception matching passthrough (ticket #33) ---
# Merged with #76's auth requirement: /attempts/check now needs a parent token too,
# so both cases below carry _mock_parent_auth()/AUTH_HEADER same as the check_attempt
# tests above - originally written pre-auth, adapted here rather than dropped.


def test_check_attempt_without_question_text_still_works():
    """question_text is optional (ticket #33) - omitting it entirely must not break
    the existing request shape."""
    with _mock_parent_auth():
        response = client.post(
            "/attempts/check",
            json={"steps": [{"recognized_latex": "5/7"}], "correct_answer": "7/12"},
            headers=AUTH_HEADER,
        )
    assert response.status_code == 200
    assert response.json()[0]["misconception_id"] is None


def test_check_attempt_with_question_text_is_accepted():
    """Confirms the field is accepted and passed through to run_pipeline without
    error - the specific matching logic itself is covered by
    test_orchestration.py's mocked-DB tests, not re-tested here. DB calls mocked
    (empty results) so this stays a unit test, not a real Supabase hit."""
    empty_client = MagicMock()
    empty_client.table.return_value.select.return_value.execute.return_value.data = []
    empty_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = (
        []
    )
    with (
        _mock_parent_auth(),
        patch("misconception_matching.get_client", return_value=empty_client),
        patch("hint_selection.get_client", return_value=empty_client),
    ):
        response = client.post(
            "/attempts/check",
            json={
                "steps": [{"recognized_latex": "5/7"}],
                "correct_answer": "7/12",
                "question_text": "1/3 + 1/4",
            },
            headers=AUTH_HEADER,
        )
    assert response.status_code == 200
