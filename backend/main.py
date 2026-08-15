import logging
import os
import time

import sentry_sdk
from dotenv import load_dotenv
from sentry_sdk.integrations.logging import LoggingIntegration
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from attempts import AttemptPersistenceError, create_attempt
from db import DatabaseError
from latex_parser import LatexParseError
from models import Attempt, EvaluationResult, Problem, Step
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
    # preview URLs). No credentials are involved (no cookies/auth headers),
    # so a broad-but-scoped-to-Vercel origin match is reasonable here.
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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


class StepCreate(BaseModel):
    recognized_latex: str
    is_correct: bool


class AttemptCreate(BaseModel):
    problem_id: int
    student_id: str
    status: str
    steps: list[StepCreate]


@app.post("/attempts", response_model=Attempt)
def create_attempt_endpoint(payload: AttemptCreate):
    try:
        return create_attempt(
            problem_id=payload.problem_id,
            student_id=payload.student_id,
            status=payload.status,
            steps=[s.model_dump() for s in payload.steps],
        )
    except AttemptPersistenceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


class CheckStep(BaseModel):
    recognized_latex: str


class CheckRequest(BaseModel):
    steps: list[CheckStep]
    correct_answer: str
    # question_text (ticket #33): the problem's own text, needed for misconception
    # matching - optional so pre-#33 callers (and existing tests) are unaffected.
    question_text: str | None = None


@app.post("/attempts/check", response_model=list[EvaluationResult])
def check_attempt(payload: CheckRequest):
    # Placeholder id/attempt_id: run_pipeline only ever reads recognized_latex - this
    # endpoint checks work before a real Attempt/Step exists to attach real ids to,
    # matching test_orchestration.py's own make_step() precedent.
    steps = [
        Step(id=0, attempt_id=0, recognized_latex=s.recognized_latex, is_correct=False)
        for s in payload.steps
    ]
    try:
        return run_pipeline(steps, correct_answer=payload.correct_answer, question_text=payload.question_text)
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
