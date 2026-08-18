@echo off
setlocal enabledelayedexpansion
title EZ-Game-Chat - Windows Setup Wizard

:: 1. Self-elevate to Administrator (required for global hotkeys in games)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to complete installation...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ====================================================
echo        EZ-Game-Chat - Installation Wizard
echo ====================================================
echo.

set "TARGET_DIR=%LocalAppData%\EZ-Game-Chat"
echo [1/3] Target installation directory:
echo       "%TARGET_DIR%"
echo.

:: 2. Copy application files & uninstaller script
echo [2/3] Installing application files...
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

if exist "%~dp0dist\EZ-Game-Chat" (
    xcopy /E /I /Y /Q "%~dp0dist\EZ-Game-Chat\*" "%TARGET_DIR%\" >nul
) else if exist "%~dp0EZ-Game-Chat.exe" (
    xcopy /E /I /Y /Q "%~dp0*" "%TARGET_DIR%\" >nul
) else (
    echo [ERROR] Could not locate bundled application files in dist folder.
    echo Please run build.bat first!
    pause
    exit /b 1
)

if exist "%~dp0uninstaller.bat" (
    copy /Y "%~dp0uninstaller.bat" "%TARGET_DIR%\uninstaller.bat" >nul
)

:: 3. Create Shortcuts
echo [3/3] Creating Start Menu and Desktop Shortcuts...

set "DESKTOP_PATH=%PUBLIC%\Desktop"
if not exist "%DESKTOP_PATH%" set "DESKTOP_PATH=%USERPROFILE%\Desktop"
set "START_MENU_PATH=%ProgramData%\Microsoft\Windows\Start Menu\Programs"
if not exist "%START_MENU_PATH%" set "START_MENU_PATH=%AppData%\Microsoft\Windows\Start Menu\Programs"

:: Desktop Shortcut
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%DESKTOP_PATH%\EZ-Game-Chat.lnk'); $s.TargetPath='%TARGET_DIR%\EZ-Game-Chat.exe'; $s.WorkingDirectory='%TARGET_DIR%'; $s.Save()"

:: Start Menu Application Shortcut
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%START_MENU_PATH%\EZ-Game-Chat.lnk'); $s.TargetPath='%TARGET_DIR%\EZ-Game-Chat.exe'; $s.WorkingDirectory='%TARGET_DIR%'; $s.Save()"

:: Start Menu Uninstaller Shortcut
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%START_MENU_PATH%\Uninstall EZ-Game-Chat.lnk'); $s.TargetPath='%TARGET_DIR%\uninstaller.bat'; $s.WorkingDirectory='%TARGET_DIR%'; $s.Save()"

echo.
echo ====================================================
echo   Installation Successful!
echo   Application installed to: %TARGET_DIR%
echo   Shortcuts created on Desktop and Start Menu.
echo   Uninstaller created: %TARGET_DIR%\uninstaller.bat
echo ====================================================
echo.

set /p LAUNCH="Do you want to start EZ-Game-Chat now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    start "" "%TARGET_DIR%\EZ-Game-Chat.exe"
)

exit /b 0
