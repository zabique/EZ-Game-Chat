@echo off
setlocal enabledelayedexpansion
title EZ-Game-Chat - Uninstaller Wizard

:: Self-elevate to Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [EZ-Game-Chat] Requesting Administrator privileges to uninstall...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ====================================================
echo        EZ-Game-Chat - Uninstaller
echo ====================================================
echo.

set "TARGET_DIR=%LocalAppData%\EZ-Game-Chat"
set /p CONFIRM="Are you sure you want to completely uninstall EZ-Game-Chat? (Y/N): "
if /i "%CONFIRM%" neq "Y" (
    echo Uninstall cancelled.
    exit /b 0
)

echo.
echo [1/3] Terminating any running EZ-Game-Chat processes...
taskkill /F /IM EZ-Game-Chat.exe >nul 2>&1

echo [2/3] Removing Desktop and Start Menu Shortcuts...
set "DESKTOP_PATH=%PUBLIC%\Desktop"
if not exist "%DESKTOP_PATH%\EZ-Game-Chat.lnk" set "DESKTOP_PATH=%USERPROFILE%\Desktop"
set "START_MENU_PATH=%ProgramData%\Microsoft\Windows\Start Menu\Programs"
if not exist "%START_MENU_PATH%\EZ-Game-Chat.lnk" set "START_MENU_PATH=%AppData%\Microsoft\Windows\Start Menu\Programs"

if exist "%DESKTOP_PATH%\EZ-Game-Chat.lnk" del /f /q "%DESKTOP_PATH%\EZ-Game-Chat.lnk" >nul 2>&1
if exist "%USERPROFILE%\Desktop\EZ-Game-Chat.lnk" del /f /q "%USERPROFILE%\Desktop\EZ-Game-Chat.lnk" >nul 2>&1
if exist "%START_MENU_PATH%\EZ-Game-Chat.lnk" del /f /q "%START_MENU_PATH%\EZ-Game-Chat.lnk" >nul 2>&1
if exist "%AppData%\Microsoft\Windows\Start Menu\Programs\EZ-Game-Chat.lnk" del /f /q "%AppData%\Microsoft\Windows\Start Menu\Programs\EZ-Game-Chat.lnk" >nul 2>&1

echo [3/3] Removing application files from "%TARGET_DIR%"...
if exist "%TARGET_DIR%" (
    :: Schedule folder removal after batch file terminates
    start /b cmd /c "timeout /t 1 /nobreak >nul & rmdir /s /q \"%TARGET_DIR%\""
)

echo.
echo ====================================================
echo   Uninstallation Complete!
echo   EZ-Game-Chat has been removed from your system.
echo ====================================================
echo.
pause
exit /b 0
