@echo off
echo Installing Claude Agent dependencies...

:: Check if Python is installed
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH! Please install Python 3.8 or newer.
    echo You can download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo Dependencies installed successfully!
echo.
echo To use the Claude Agent, run:
echo   venv\Scripts\activate.bat
echo   python agent.py --query "Your query here"
echo.

pause
