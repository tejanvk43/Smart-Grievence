@echo off
echo ==========================================
echo    Smart Grievance - Application Startup
echo ==========================================
echo.

echo Starting Backend Server...
start "Smart Griev Backend" cmd /k "cd backend && if exist venv (call venv\Scripts\activate) else (echo Venv not found, running with system python) && python app.py"

echo Starting Frontend Server...
start "Smart Griev Frontend" cmd /k "npm run dev"

echo.
echo Application is starting...
echo Backend will run on http://localhost:5000
echo Frontend will run on http://localhost:3000 (usually)
echo.
echo Close the popup windows to stop the servers.
pause
