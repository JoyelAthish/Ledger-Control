@echo off
echo ============================================
echo   Starting Ledger Control
echo ============================================
echo.

REM Start backend in its own window
start "Ledger Control - Backend" cmd /k "cd /d %~dp0backend && call ..\myenv\Scripts\activate && uvicorn main:app --reload --port 8000"

REM Give the backend a few seconds to boot before starting the frontend
timeout /t 4 /nobreak >nul

REM Start frontend in its own window
start "Ledger Control - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Backend starting at:  http://localhost:8000
echo Frontend starting at: http://localhost:5173
echo.
echo Two windows just opened - one for each server. Leave both running.
echo Close this window any time; it's not needed once the other two are up.
pause
