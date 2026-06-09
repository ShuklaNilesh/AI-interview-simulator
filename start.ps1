# InterviewAce AI Startup Launcher

Write-Host "=============================================" -ForegroundColor Indigo
Write-Host "   Starting InterviewAce AI Application Stack   " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Indigo

# Start Backend Server in a new window
Write-Host "[1/2] Spinning up FastAPI backend on http://localhost:8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\activate; uvicorn backend.main:app --reload --port 8000"

# Start Frontend Server in a new window
Write-Host "[2/2] Launching Next.js frontend dev server on http://localhost:3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "Applications launched!" -ForegroundColor Green
Write-Host "- Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "- Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Indigo
