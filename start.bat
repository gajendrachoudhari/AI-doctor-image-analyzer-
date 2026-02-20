@echo off
cd /d "%~dp0"

echo ========================================
echo   Starting AI-DOCTOR System...
echo ========================================
echo.

REM --- Configure PORTS ---
set FASTAPI_PORT=8007
set HTML_PORT=5500

echo Backend API will run on: http://localhost:%FASTAPI_PORT%
echo Frontend will run on:   http://localhost:%HTML_PORT%/templates/index.html
echo.

set "PROJECT_DIR=%~dp0"
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

REM --- Start FastAPI Backend ---
echo Starting FastAPI backend...
start "FastAPI Backend" cmd /k "cd /d ""%PROJECT_DIR%"" && python -m uvicorn app:app --reload --host 0.0.0.0 --port %FASTAPI_PORT%"
timeout /t 3 /nobreak >nul

REM --- Start HTML Server ---
echo Starting HTML server...
start "HTML Server" cmd /k "cd /d ""%PROJECT_DIR%"" && python -m http.server %HTML_PORT%"
timeout /t 2 /nobreak >nul

REM --- Open Browser ---
echo Opening your browser...
timeout /t 2 /nobreak >nul
start "" "http://localhost:%HTML_PORT%/templates/index.html"

echo.
echo ========================================
echo   System started successfully!
echo ========================================
echo.
echo Backend API: http://localhost:%FASTAPI_PORT%
echo Frontend:    http://localhost:%HTML_PORT%/templates/index.html
echo.
echo Press any key to exit this window...
echo (The servers will continue running)
pause >nul