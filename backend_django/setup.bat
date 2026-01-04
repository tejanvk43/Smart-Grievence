@echo off
echo Setting up Django Backend for Smart Griev...

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
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
echo Seeding database with departments...
python manage.py seed_db

echo.
echo Setup complete!
echo.
echo To start the server, run:
echo   venv\Scripts\activate
echo   python manage.py runserver 0.0.0.0:5000

pause
