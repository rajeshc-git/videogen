@echo off
title VidGen - MiniMax H3 Localhost:7860
cd /d "%~dp0"

echo ====================================================
echo   VidGen - MiniMax H3 Native Audio ^& Video Studio
echo ====================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your system PATH!
    echo Please install Python 3.10+ and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

python -c "import fastapi, uvicorn, requests, websockets, PIL" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing required packages from requirements.txt...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo.
)

echo Starting VidGen server on http://localhost:7860...
echo.

python server.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] VidGen server stopped unexpectedly.
    pause
)
