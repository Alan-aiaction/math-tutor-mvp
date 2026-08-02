# Starts both the backend (FastAPI/uvicorn) and frontend (Next.js) dev servers,
# each in its own window so logs stay visible and either can be stopped
# independently with Ctrl+C. Opens the browser once both are up.

$repoRoot = $PSScriptRoot

Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$repoRoot\backend'; Write-Host 'Backend (FastAPI) - http://localhost:8000' -ForegroundColor Green; .venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000"
)

Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "cd '$repoRoot\frontend'; Write-Host 'Frontend (Next.js) - http://localhost:3000' -ForegroundColor Cyan; npm.cmd run dev"
)

Write-Host "Starting backend (port 8000) and frontend (port 3000) in separate windows..."
Start-Sleep -Seconds 6
Start-Process "http://localhost:3000"
