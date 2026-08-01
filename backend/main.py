from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from recognition import RecognitionError, recognize_math

load_dotenv()

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
    stroke_groups = [g.model_dump(exclude_none=True) for g in payload.strokeGroups]
    try:
        latex = recognize_math(stroke_groups, width=payload.width, height=payload.height)
    except RecognitionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return RecognizeResponse(latex=latex)
