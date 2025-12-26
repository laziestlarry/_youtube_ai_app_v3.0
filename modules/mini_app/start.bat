@echo off
cls

echo 🚀 YouTube Income Commander v2.0
echo ==================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+
    echo    Download from: https://python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if we're in the right directory
if not exist "cli_launcher.py" (
    echo ❌ cli_launcher.py not found.
    echo    Please run this script from the YouTube Income Commander directory.
    pause
    exit /b 1
)

REM Check if system is installed
if not exist "config\main_config.json" (
    echo 🔧 System not installed. Running installer...
    python install.py
    
    if %errorlevel% neq 0 (
        echo ❌ Installation failed. Please check the errors above.
        pause
        exit /b 1
    )
)

REM Check for virtual environment
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
if exist "requirements.txt" (
    echo 📦 Checking dependencies...
    pip install -r requirements.txt --quiet --upgrade
)

REM Start the system
echo 🎬 Starting YouTube Income Commander...
echo.
echo Choose your preferred interface:
echo 1. Command Line Interface (CLI)
echo 2. Web Interface (Browser)
echo 3. Quick Demo
echo 4. System Status
echo.

set /p choice="Enter choice (1-4) [1]: "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo 🖥️  Starting CLI...
    python cli_launcher.py
) else if "%choice%"=="2" (
    echo 🌐 Starting web server...
    echo    Server will be available at: http://127.0.0.1:8000
    echo    Press Ctrl+C to stop
    echo.
    cd backend 2>nul
    python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
    cd ..
) else if "%choice%"=="3" (
    echo 🎯 Starting quick demo...
    python quick_demo.py
) else if "%choice%"=="4" (
    echo 📊 System status...
    python -c "from version_info import print_version_banner, print_system_status; print_version_banner(); print_system_status()"
) else (
    echo ❌ Invalid choice. Starting CLI...
    python cli_launcher.py
)

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat 2>nul

echo.
echo 👋 Thanks for using YouTube Income Commander!
echo    For support, run: python cli_launcher.py help
pause