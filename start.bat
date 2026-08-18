@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: Self-elevate to Administrator if not already elevated (required for in-game hotkeys)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [EZ-Game-Chat] Requesting Administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

title EZ-Game-Chat Auto-Typer

:: Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [EZ-Game-Chat] Setting up virtual environment...
    
    where uv >nul 2>&1
    if !errorlevel! equ 0 (
        echo Using uv to create virtual environment...
        uv venv .venv
        uv pip install -r requirements.txt --python .venv
    ) else (
        where python >nul 2>&1
        if !errorlevel! equ 0 (
            echo Using system Python to create virtual environment...
            python -m venv .venv
            .venv\Scripts\python -m pip install --upgrade pip
            .venv\Scripts\python -m pip install -r requirements.txt
        ) else (
            echo [ERROR] Neither Python nor UV was found in system PATH.
            echo Please install Python 3.10+ or UV to run this application.
            pause
            exit /b 1
        )
    )
)

echo [EZ-Game-Chat] Starting Application...
.venv\Scripts\python main.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with code %errorlevel%.
    pause
)
