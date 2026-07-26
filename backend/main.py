from fastapi import FastAPI

app = FastAPI(title="Math Tutor MVP Backend")


@app.get("/")
def root():
    return {"status": "ok", "message": "Math Tutor MVP backend — placeholder, real API coming in Phase 2"}


@app.get("/health")
def health():
    return {"status": "healthy"}
