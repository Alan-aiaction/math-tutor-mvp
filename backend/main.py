import logging
import os
import time
from dataclasses import dataclass

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.logging import LoggingIntegration
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from attempts import AttemptPersistenceError, create_attempt
from auth import AuthError, get_current_child, get_current_parent_id, issue_child_token
from children import (
    ChildError,
    create_child,
    delete_child,
    get_child,
    get_child_by_nickname,
    list_children,
    verify_child_login,
)
from db import DatabaseError
from feedback import create_feedback
from kpis import (
    get_accuracy_trend,
    get_average_retries,
    get_practice_frequency,
    get_total_attempts,
    get_weak_spots_by_topic,
)
from latex_parser import LatexParseError
from models import Attempt, Child, EvaluationResult, Feedback, Problem, Step
from orchestration import run_pipeline
from parents import get_or_create_parent, get_parent_by_family_code
from problems import ProblemNotFoundError, get_problem, get_random_problem
from recognition import RecognitionError, recognize_math

load_dotenv()

# Task #16: nothing in this app ever called basicConfig before this - logger.info() calls
# (db.py, orchestration.py) were being silently dropped (default level is WARNING), and
# logger.error() calls printed with no timestamp/structure. This is the actual fix: configures
# the root logger once, which every module's logging.getLogger(__name__) inherits.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# Task #59: send_default_pii=False (not Sentry's suggested True) - this app handles minors'
# data, matching the GDPR-for-minors stance behind #49. A missing SENTRY_DSN (e.g. a
# teammate's local env) makes this a documented no-op, not an error.
#
# event_level=None on the logging integration: Sentry's default would turn every
# logger.error() call (db.py's missing-credentials error, DatabaseError, etc.) into its own
# Sentry event - those are already-handled, already-logged cases (see #59's plan), not
# "something broke unexpectedly." The one deliberate signal this ticket wants is the explicit
# capture_exception() call in unhandled_exception_handler below.
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    send_default_pii=False,
    integrations=[LoggingIntegration(level=logging.INFO, event_level=None)],
)

app = FastAPI(title="Math Tutor Backend")

app.add_middleware(
    CORSMiddleware,
    # Local dev, plus every Vercel deployment for this project (prod + all
    # preview URLs). Authorization is required (ticket #76's parent/child auth
    # sends Bearer tokens on every request that needs a parent identity) - no
    # cookies/TLS-client-certs are used, so allow_credentials stays False.
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.2fms)", request.method, request.url.path, response.status_code, duration_ms)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Only reached for exceptions a route didn't already convert to HTTPException itself
    # (e.g. RecognitionError -> 502) - FastAPI's built-in HTTPException handler takes
    # priority over this one, so existing per-route error mapping is unaffected.
    # This custom handler replaces Starlette's default exception-handling middleware, which
    # is what Sentry's FastAPI integration normally hooks into - so capture_exception must be
    # called explicitly here, or these errors would never reach Sentry (#59).
    sentry_sdk.capture_exception(exc)
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def require_parent_id(authorization: str | None = Header(None)) -> str:
    """FastAPI dependency (ticket #children-auth, 3rd MVP): verifies the parent's
    Supabase access token and returns their user id, or raises a clean 401. Used by
    every route that acts on behalf of a parent - see auth.py for the actual
    verification."""
    try:
        return get_current_parent_id(authorization)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@dataclass
class Requester:
    """Either a parent (acting on behalf of a child they've picked) or an
    independently-logged-in child (PR 2/3) - exactly one of parent_id/child_id is set."""

    parent_id: str | None
    child_id: int | None


def require_requester(authorization: str | None = Header(None)) -> Requester:
    """Accepts either a child's own session token OR a parent's Supabase token - used
    only on the two endpoints an independent child's practice session actually needs
    (POST /attempts, POST /attempts/check). Everything else (dashboard, account
    management, /children CRUD) stays strictly parent-only via require_parent_id above.

    Tries the child token first: it's a local signature check, no network round-trip,
    unlike the parent path below - cheaper for the common case once independent child
    login exists, and a real Supabase token can never verify as a child token anyway
    (different signing key), so trying it first changes nothing about which requests
    succeed."""
    try:
        child = get_current_child(authorization)
        return Requester(parent_id=child.parent_id, child_id=child.child_id)
    except AuthError:
        pass
    try:
        parent_id = get_current_parent_id(authorization)
        return Requester(parent_id=parent_id, child_id=None)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@app.get("/")
def root():
    return {"status": "ok", "message": "Math Tutor backend — placeholder, real API coming in Phase 2"}


@app.get("/health")
def health():
    return {"status": "healthy"}


class Stroke(BaseModel):
    x: list[float]
    y: list[float]
    t: list[float]
    pointerType: str | None = None


class StrokeGroup(BaseModel):
    penStyle: dict | None = None
    strokes: list[Stroke]


class RecognizeRequest(BaseModel):
    strokeGroups: list[StrokeGroup]
    width: int
    height: int


class RecognizeResponse(BaseModel):
    latex: str


@app.post("/recognize", response_model=RecognizeResponse)
def recognize(payload: RecognizeRequest):
    # Privacy invariant (task #49): raw strokeGroups are never persisted or logged past
    # this request - only the returned LaTeX matters. Keep it that way when #13/#15 land:
    # attempt_steps should store recognized_latex only, never stroke coordinates.
    stroke_groups = [g.model_dump(exclude_none=True) for g in payload.strokeGroups]
    try:
        latex = recognize_math(stroke_groups, width=payload.width, height=payload.height)
    except RecognitionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return RecognizeResponse(latex=latex)


class ChildCreate(BaseModel):
    nickname: str
    password: str


class ParentProfile(BaseModel):
    family_code: str
    max_children: int
    children_count: int


@app.get("/parents/me", response_model=ParentProfile)
def get_parent_profile_endpoint(parent_id: str = Depends(require_parent_id)):
    parent = get_or_create_parent(parent_id)
    children_count = len(list_children(parent_id))
    return ParentProfile(family_code=parent.family_code, max_children=parent.max_children, children_count=children_count)


@app.post("/children", response_model=Child)
def create_child_endpoint(payload: ChildCreate, parent_id: str = Depends(require_parent_id)):
    try:
        return create_child(parent_id, payload.nickname, payload.password)
    except ChildError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/children", response_model=list[Child])
def list_children_endpoint(parent_id: str = Depends(require_parent_id)):
    return list_children(parent_id)


@app.delete("/children/{child_id}")
def delete_child_endpoint(child_id: int, parent_id: str = Depends(require_parent_id)):
    if get_child(parent_id, child_id) is None:
        raise HTTPException(status_code=403, detail="This child does not belong to the authenticated parent")
    delete_child(parent_id, child_id)
    # {"deleted": true} rather than 204 No Content - apiFetch.js always calls res.json(),
    # which would throw on an empty body and get reported as a generic network error.
    return {"deleted": True}


class ChildLogin(BaseModel):
    password: str


class ChildLoginSession(BaseModel):
    child: Child
    token: str


@app.post("/children/{child_id}/login", response_model=ChildLoginSession)
def child_login_endpoint(child_id: int, payload: ChildLogin, parent_id: str = Depends(require_parent_id)):
    # Deliberately the same 401 for "not this parent's child" and "wrong password" -
    # neither should let a caller distinguish which one it was (see children.py's
    # verify_child_login docstring).
    if not verify_child_login(parent_id, child_id, payload.password):
        raise HTTPException(status_code=401, detail="Incorrect child password")
    child = get_child(parent_id, child_id)
    # Retire-active-child: this endpoint now issues a real child session token too, the
    # same shape independent login returns - a parent picking a child from Mijn kinderen
    # and a child logging in on their own device both converge on the same downstream
    # session, instead of this path setting the old (now-removed) activeChild instead.
    token = issue_child_token(child_id=child.id, parent_id=parent_id)
    return ChildLoginSession(child=child, token=token)


class ChildIndependentLogin(BaseModel):
    family_code: str
    nickname: str
    password: str


@app.post("/children/login", response_model=ChildLoginSession)
def child_independent_login_endpoint(payload: ChildIndependentLogin):
    """Independent child login (PR 2 of 3) - no parent session required at all. A child
    proves who they are with family_code + nickname + password (see decision-log.md for
    why family_code, not a globally-unique nickname); a matching login issues them their
    own short-lived token (auth.issue_child_token) to use on every later practice
    request instead of a parent's Bearer token.

    Every failure - unknown family code, unknown nickname, wrong password - collapses to
    the same generic 401, same enumeration-avoidance principle as the existing
    parent-mediated child_login_endpoint above."""
    generic_error = HTTPException(status_code=401, detail="Incorrect login")

    parent = get_parent_by_family_code(payload.family_code)
    if parent is None:
        raise generic_error

    child = get_child_by_nickname(parent.id, payload.nickname)
    if child is None or not verify_child_login(parent.id, child.id, payload.password):
        raise generic_error

    token = issue_child_token(child_id=child.id, parent_id=parent.id)
    return ChildLoginSession(child=child, token=token)


class StepCreate(BaseModel):
    recognized_latex: str
    is_correct: bool
    # previous_wrong_count (KPI data layer): same field name/semantics as CheckStep's
    # existing field (ticket #71) - how many times this step already came back wrong
    # before this save. Persisted now instead of discarded, so retry-rate KPIs are
    # computable later.
    previous_wrong_count: int = 0


class AttemptCreate(BaseModel):
    problem_id: int
    child_id: int
    status: str
    steps: list[StepCreate]


@app.post("/attempts", response_model=Attempt)
def create_attempt_endpoint(payload: AttemptCreate, requester: Requester = Depends(require_requester)):
    if requester.child_id is not None:
        # An independent child's own token already proves ownership - just confirm
        # they're not posting under a sibling's child_id (403, not silently corrected).
        if requester.child_id != payload.child_id:
            raise HTTPException(status_code=403, detail="This child does not belong to the authenticated parent")
    elif get_child(requester.parent_id, payload.child_id) is None:
        raise HTTPException(status_code=403, detail="This child does not belong to the authenticated parent")
    try:
        return create_attempt(
            problem_id=payload.problem_id,
            child_id=payload.child_id,
            status=payload.status,
            steps=[s.model_dump() for s in payload.steps],
        )
    except AttemptPersistenceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


class ChildKpis(BaseModel):
    accuracy_trend: list[dict]
    practice_frequency_days: int
    average_retries: float
    weak_spots_by_topic: list[dict]
    total_attempts: int


@app.get("/children/{child_id}/kpis", response_model=ChildKpis)
def get_child_kpis_endpoint(child_id: int, requester: Requester = Depends(require_requester)):
    # require_requester (not require_parent_id): a child's own dashboard (own-data-only,
    # never a sibling's) needs to fetch this with just their own session token - same
    # ownership pattern POST /attempts already uses.
    if requester.child_id is not None:
        if requester.child_id != child_id:
            raise HTTPException(status_code=403, detail="This child does not belong to the authenticated parent")
    elif get_child(requester.parent_id, child_id) is None:
        raise HTTPException(status_code=403, detail="This child does not belong to the authenticated parent")
    return ChildKpis(
        accuracy_trend=get_accuracy_trend(child_id),
        practice_frequency_days=get_practice_frequency(child_id),
        average_retries=get_average_retries(child_id),
        weak_spots_by_topic=get_weak_spots_by_topic(child_id),
        total_attempts=get_total_attempts(child_id),
    )


class CheckStep(BaseModel):
    recognized_latex: str
    # previous_wrong_count (ticket #71): how many times this step already came
    # back wrong in this same problem-solving session, tracked client-side - see
    # orchestration.py's module docstring for why the backend doesn't infer this
    # from persisted attempt history instead. Defaults to 0 (first try).
    previous_wrong_count: int = 0


class CheckRequest(BaseModel):
    steps: list[CheckStep]
    correct_answer: str
    # question_text (ticket #33): the problem's own text, needed for misconception
    # matching - optional so pre-#33 callers (and existing tests) are unaffected.
    question_text: str | None = None


@app.post("/attempts/check", response_model=list[EvaluationResult])
def check_attempt(payload: CheckRequest, requester: Requester = Depends(require_requester)):
    # requester.parent_id IS used here (for the per-account LLM token limit, on any
    # live escalated-hint call) even though nothing else on this stateless endpoint
    # touches the children/attempts tables - the dependency itself is still also what
    # keeps this endpoint from being hit anonymously, consistent with the rest of the
    # app. require_requester (not require_parent_id) so an independent child's own
    # token works here too - a child's practice session needs to check their work
    # without ever having a parent session at all; Requester.parent_id is populated
    # either way (see its own docstring).
    #
    # Placeholder id/attempt_id: run_pipeline only ever reads recognized_latex - this
    # endpoint checks work before a real Attempt/Step exists to attach real ids to,
    # matching test_orchestration.py's own make_step() precedent.
    steps = [
        Step(id=0, attempt_id=0, recognized_latex=s.recognized_latex, is_correct=False)
        for s in payload.steps
    ]
    try:
        return run_pipeline(
            steps,
            correct_answer=payload.correct_answer,
            question_text=payload.question_text,
            previous_wrong_counts=[s.previous_wrong_count for s in payload.steps],
            parent_id=requester.parent_id,
        )
    except LatexParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # PipelineError is deliberately not caught here - it signals a genuine unexpected bug
    # (per orchestration.py's own docstring), not bad input, so it falls through to the
    # global unhandled_exception_handler (#16) for logging, Sentry capture, and a clean 500.


class FeedbackCreate(BaseModel):
    rating: int
    category: str | None = None
    message: str | None = None


@app.post("/feedback", response_model=Feedback)
def create_feedback_endpoint(payload: FeedbackCreate, requester: Requester = Depends(require_requester)):
    # require_requester (not require_parent_id): a child submits feedback with their
    # own session token, same as /attempts and /attempts/check - requester.child_id
    # is set only then, requester.parent_id either way, so the row is attributed
    # correctly without the frontend needing to say which role it is.
    if not 1 <= payload.rating <= 5:
        raise HTTPException(status_code=400, detail="rating must be between 1 and 5")
    return create_feedback(
        parent_id=requester.parent_id,
        child_id=requester.child_id,
        rating=payload.rating,
        category=payload.category,
        message=payload.message,
    )


# Must be registered before /problems/{problem_id} - otherwise Starlette matches
# "random" against that route's path pattern first and fails int coercion (422)
# before this handler is ever reached.
@app.get("/problems/random", response_model=Problem)
def get_random_problem_endpoint():
    try:
        return get_random_problem()
    except ProblemNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/problems/{problem_id}", response_model=Problem)
def get_problem_endpoint(problem_id: int):
    try:
        return get_problem(problem_id)
    except ProblemNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
