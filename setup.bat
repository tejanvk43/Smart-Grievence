@echo off
echo ================================
echo Smart Griev - Windows Setup
echo ================================
echo.

REM Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo Python found!

REM Setup Backend
echo.
echo [2/4] Setting up Backend...
cd backend_django

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment and install dependencies
echo Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt

REM Download NLTK data
echo Downloading NLP data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)"

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Seed database
echo Seeding database with initial data...
python manage.py seed_db

echo Backend setup complete!
cd ..

REM Setup Frontend
echo.
echo [3/4] Setting up Frontend...

REM Check for pnpm or npm
where pnpm >nul 2>&1
if %errorlevel% equ 0 (
    set PKG_MANAGER=pnpm
    echo Using pnpm
) else (
    where npm >nul 2>&1
    if %errorlevel% equ 0 (
        set PKG_MANAGER=npm
        echo Using npm
    ) else (
        echo ERROR: Neither pnpm nor npm found
        echo Please install Node.js from https://nodejs.org/
        pause
        exit /b 1
    )
)

REM Install frontend dependencies
if not exist "node_modules" (
    echo Installing frontend dependencies...
    %PKG_MANAGER% install
)

echo Frontend setup complete!

REM Print summary
echo.
echo [4/4] Setup Complete!
echo ================================
echo.
echo Default Admin Credentials:
echo   Email: admin@smartgriev.com
echo   Password: Admin@123
echo.
echo To start the application:
echo   Run: run.bat
echo.
echo Or manually:
echo   Terminal 1: cd backend_django ^&^& venv\Scripts\activate ^&^& python manage.py runserver 0.0.0.0:8000
echo   Terminal 2: pnpm dev (or npm run dev)
echo.
echo ================================
pause
