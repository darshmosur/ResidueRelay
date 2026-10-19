# ResidueRelay Dual Service Launcher
Write-Host "===================================================" -ForegroundColor Green
Write-Host "      🌾 Starting ResidueRelay Platform" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "[1/2] Launching Python FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python run.py"

Start-Sleep -Seconds 2

Write-Host "[2/2] Launching Next.js Frontend Dashboard on http://localhost:3000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host " ResidueRelay Services are running!" -ForegroundColor Green
Write-Host " Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host " Backend:  http://localhost:8000/docs (Swagger UI)" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Green
