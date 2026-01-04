@echo off
echo =========================================
echo Smart Griev - Complete Setup
echo =========================================
echo.

REM Frontend Setup
echo [1/2] Setting up Frontend...
echo Installing frontend dependencies...
call pnpm install

echo.
echo [2/2] Setting up Django Backend...
cd backend_django

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"

REM Run migrations
echo Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Seed database
echo Seeding database...
python manage.py seed_db

cd ..

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo To run the project, open TWO terminals:
echo.
echo Terminal 1 (Frontend):
echo   pnpm dev
echo.
echo Terminal 2 (Backend):
echo   cd backend_django
echo   venv\Scripts\activate
echo   python manage.py runserver 0.0.0.0:5000
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:5000
echo =========================================

pause
