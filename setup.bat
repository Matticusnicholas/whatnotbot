@echo off
title Whatnot Giveaway Bot - Setup
color 0A

echo ========================================
echo   Whatnot Giveaway Bot - Windows Setup
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

:: Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip is not available!
    echo Please reinstall Python with pip included.
    pause
    exit /b 1
)

echo [OK] pip found:
pip --version
echo.

:: Create virtual environment
echo [INFO] Creating virtual environment...
if exist "venv" (
    echo [INFO] Virtual environment already exists, skipping creation.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)
echo.

:: Activate virtual environment and install dependencies
echo [INFO] Installing dependencies...
call venv\Scripts\activate.bat

pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [OK] All dependencies installed successfully!
echo.

:: Check for Firefox
echo [INFO] Checking for Firefox browser...
if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
    echo [OK] Firefox found at: %ProgramFiles%\Mozilla Firefox\firefox.exe
) else if exist "%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe" (
    echo [OK] Firefox found at: %ProgramFiles(x86)%\Mozilla Firefox\firefox.exe
) else (
    echo [WARNING] Firefox not found in default location.
    echo          Please ensure Firefox is installed for the bot to work.
    echo          Download from: https://www.mozilla.org/firefox/
)
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To start the bot, run: run.bat
echo Or double-click run.bat in File Explorer
echo.
pause
