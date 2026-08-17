import logging
import os
import time

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.logging import LoggingIntegration
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from attempts import AttemptPersistenceError, create_attempt
from auth import AuthError, get_current_parent_id
from children import ChildError, create_child, get_child, list_children, verify_child_login
from db import DatabaseError
from kpis import get_accuracy_trend, get_average_retries, get_practice_frequency, get_weak_spots_by_topic
from latex_parser import LatexParseError
from models import Attempt, Child, EvaluationResult, Problem, Step
from orchestration import run_pipeline
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

app = FastAPI(title="Math Tutor MVP Backend")

app.add_middleware(
    CORSMiddleware,
    # Local dev, plus every Vercel deployment for this project (prod + all
    # preview URLs). Authorization is required (ticket #76's parent/child auth
    # sends Bearer tokens on every request that needs a parent identity) - no
    # cookies/TLS-client-certs are used, so allow_credentials stays False.
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["GET", "POST"],
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


@app.get("/")
def root():
    return {"status": "ok", "message": "Math Tutor MVP backend — placeholder, real API coming in Phase 2"}


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


@app.post("/children", response_model=Child)
def create_child_endpoint(payload: ChildCreate, parent_id: str = Depends(require_parent_id)):
    try:
        return create_child(parent_id, payload.nickname, payload.password)
    except ChildError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/children", response_model=list[Child])
def list_children_endpoint(parent_id: str = Depends(require_parent_id)):
    return list_children(parent_id)


class ChildLogin(BaseModel):
    password: str


@app.post("/children/{child_id}/login", response_model=Child)
def child_login_endpoint(child_id: int, payload: ChildLogin, parent_id: str = Depends(require_parent_id)):
    # Deliberately the same 401 for "not this parent's child" and "wrong password" -
    # neither should let a caller distinguish which one it was (see children.py's
    # verify_child_login docstring).
    if not verify_child_login(parent_id, child_id, payload.password):
        raise HTTPException(status_code=401, detail="Incorrect child password")
    child = get_child(parent_id, child_id)
    return child


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
def create_attempt_endpoint(payload: AttemptCreate, parent_id: str = Depends(require_parent_id)):
    if get_child(parent_id, payload.child_id) is None:
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


@app.get("/children/{child_id}/kpis", response_model=ChildKpis)
def get_child_kpis_endpoint(child_id: int, parent_id: str = Depends(require_parent_id)):
    if get_child(parent_id, child_id) is None:
        raise HTTPException(status_code=403, detail="This child does not belong to the authenticated parent")
    return ChildKpis(
        accuracy_trend=get_accuracy_trend(child_id),
        practice_frequency_days=get_practice_frequency(child_id),
        average_retries=get_average_retries(child_id),
        weak_spots_by_topic=get_weak_spots_by_topic(child_id),
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
def check_attempt(payload: CheckRequest, parent_id: str = Depends(require_parent_id)):
    # parent_id isn't used directly here (this endpoint is stateless, computational -
    # it never touches the children/attempts tables) - the dependency is still applied
    # so the endpoint can't be hit anonymously, consistent with the rest of the app.
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
        )
    except LatexParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # PipelineError is deliberately not caught here - it signals a genuine unexpected bug
    # (per orchestration.py's own docstring), not bad input, so it falls through to the
    # global unhandled_exception_handler (#16) for logging, Sentry capture, and a clean 500.


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
