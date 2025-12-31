@echo off
title Whatnot Giveaway Bot
color 0B

echo ========================================
echo   Whatnot Giveaway Bot - Starting...
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check if dependencies are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Dependencies not installed!
    echo Please run setup.bat first.
    echo.
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo [INFO] Starting web server...
echo.
echo ========================================
echo   Open your browser and go to:
echo   http://localhost:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server.
echo.

:: Start the Flask application
python app.py

:: If we get here, the server stopped
echo.
echo [INFO] Server stopped.
pause
