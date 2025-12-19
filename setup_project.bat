@echo off
echo ==========================================
echo    Smart Grievance - Project Setup
echo ==========================================
echo.

echo [1/3] Checking prerequisites...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.x and add it to PATH.
    pause
    exit /b
)
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo Node.js/npm is not installed. Please install Node.js.
    pause
    exit /b
)

echo [2/3] Setting up Backend...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)
echo Activating virtual environment...
call venv\Scripts\activate
echo Installing Python dependencies...
pip install -r requirements.txt
echo Downloading NLTK data...
python download_nltk.py
cd ..

echo [3/3] Setting up Frontend...
if not exist node_modules (
    echo Installing Node dependencies...
    call npm install
) else (
    echo Node modules already exist. Skipping install.
)

echo.
echo ==========================================
echo       Setup Completed Successfully!
echo ==========================================
echo.
echo You can now run the project using 'run_project.bat'
echo.
pause
