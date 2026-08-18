@echo off
cd /d "%~dp0"
title Building EZ-Game-Chat Installer

echo [1/2] Building standalone binary with PyInstaller...
.venv\Scripts\python.exe build_installer.py

if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller build failed with code %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo [2/2] Compiling Inno Setup EXE Installer...
set "ISCC_PATH=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_PATH%" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if exist "%ISCC_PATH%" (
    "%ISCC_PATH%" setup.iss
) else (
    echo [NOTE] ISCC.exe not found in standard paths. Skipping Inno Setup compile.
)

echo.
echo ====================================================
echo   Build Completed Successfully!
echo   Standalone EXE: dist\EZ-Game-Chat\EZ-Game-Chat.exe
echo   Inno Setup Installer: Output\EZ-Game-Chat_Setup.exe
echo ====================================================
echo.
pause
