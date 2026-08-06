import logging
import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from recognition import RecognitionError, recognize_math

load_dotenv()

# Task #16: nothing in this app ever called basicConfig before this - logger.info() calls
# (db.py, orchestration.py) were being silently dropped (default level is WARNING), and
# logger.error() calls printed with no timestamp/structure. This is the actual fix: configures
# the root logger once, which every module's logging.getLogger(__name__) inherits.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

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
