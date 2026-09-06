@echo off
setlocal
cd /d %~dp0

echo ============================================
echo   Ledger Control - Setup and Launch
echo ============================================
echo.

REM --- 1. Backend virtual environment ---
if not exist "myenv\Scripts\activate.bat" (
    echo [1/5] No virtual environment found - creating one...
    py -m venv myenv
) else (
    echo [1/5] Virtual environment already exists - skipping creation.
)

echo [2/5] Installing backend dependencies (safe to re-run)...
call myenv\Scripts\activate.bat
pip install -r backend\requirements.txt --quiet

REM --- 2. .env file check ---
if not exist ".env" (
    echo.
    echo [3/5] No .env file found. Creating one from .env.example...
    copy .env.example .env >nul
    echo.
    echo ============================================
    echo   ACTION NEEDED
    echo ============================================
    echo A .env file was just created, but it has a PLACEHOLDER key.
    echo Open .env in Notepad now, replace the placeholder with your
    echo own Gemini API key, save it, then run this script again.
    echo.
    notepad .env
    pause
    exit /b
) else (
    echo [3/5] .env file already exists - skipping.
)

REM --- 3. Frontend dependencies ---
if not exist "frontend\node_modules" (
    echo [4/5] Frontend packages not found - installing (this may take a minute)...
    cd frontend
    call npm install
    cd ..
) else (
    echo [4/5] Frontend packages already installed - skipping.
)

REM --- 4. Launch both servers ---
echo [5/5] Starting servers...
echo.

start "Ledger Control - Backend" cmd /k "cd /d %~dp0backend && call ..\myenv\Scripts\activate && uvicorn main:app --reload --port 8000"

timeout /t 4 /nobreak >nul

start "Ledger Control - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 6 /nobreak >nul

start http://localhost:5173

echo.
echo Backend running at:  http://localhost:8000
echo Frontend running at: http://localhost:5173
echo.
echo Two windows just opened - one for each server. Leave both running.
echo Close this window any time; it's not needed once the other two are up.
pause
