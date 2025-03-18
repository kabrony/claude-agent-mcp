@echo off
setlocal enabledelayedexpansion

:: Set title
title OrganiX Claude Agent Launcher

:: Check for Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.8 or newer.
    echo You can download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Setting up...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Check for dependencies
pip show rich >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install dependencies.
        pause
        exit /b 1
    )
)

:: Clear the screen
cls

:: Display menu
echo.
echo ===================================
echo    OrganiX Claude Agent Launcher
echo ===================================
echo.
echo Select an option:
echo 1. Launch Terminal Dashboard
echo 2. Launch Web Dashboard
echo 3. Launch CLI Agent
echo 4. Manage Environment
echo 5. Run Memory Maintenance
echo 6. Install/Update Dependencies
echo 7. Exit
echo.

:: Get user input
set /p choice="Enter your choice (1-7): "

:: Process choice
if "%choice%"=="1" (
    cls
    echo Launching Terminal Dashboard...
    python dashboard.py
) else if "%choice%"=="2" (
    cls
    echo Launching Web Dashboard...
    echo This will start a web server on http://localhost:8080
    echo Press Ctrl+C to stop the server.
    echo.
    python web_server.py
) else if "%choice%"=="3" (
    cls
    echo Launching CLI Agent...
    echo Type your query after the prompt.
    echo Press Ctrl+C to exit.
    echo.
    python agent.py
) else if "%choice%"=="4" (
    cls
    echo Environment Management
    python model_manager.py interactive
    :: Return to this menu after exiting model manager
    call %0
) else if "%choice%"=="5" (
    cls
    echo Running Memory Maintenance...
    python agent.py --maintenance
    pause
    :: Return to this menu
    call %0
) else if "%choice%"=="6" (
    cls
    echo Installing/Updating Dependencies...
    pip install -r requirements.txt
    echo.
    echo Dependencies installed/updated.
    pause
    :: Return to this menu
    call %0
) else if "%choice%"=="7" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    pause
    :: Return to this menu
    call %0
)

endlocal
