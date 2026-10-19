@echo off
title ResidueRelay Launcher
echo ===================================================
echo       🌾 Starting ResidueRelay Platform
echo ===================================================
echo.

:: Refresh environment path for Node and Python
set "PATH=%LOCALAPPDATA%\Programs\Python\Python314;%LOCALAPPDATA%\Programs\Python\Python314\Scripts;%ProgramFiles%\nodejs;%PATH%"

echo [1/2] Launching Python FastAPI Backend on http://localhost:8000 ...
start "ResidueRelay Backend" cmd /k "cd backend && python run.py"

echo [2/2] Launching Next.js Frontend Dashboard on http://localhost:3000 ...
start "ResidueRelay Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo  Services started!
echo  Backend:  http://localhost:8000/docs
echo  Frontend: http://localhost:3000
echo ===================================================
echo.
pause
