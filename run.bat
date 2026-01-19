@echo off
echo ================================
echo Smart Griev - Starting Servers
echo ================================
echo.

REM Check if setup was run
if not exist "backend_django\venv" (
    echo ERROR: Backend not set up. Please run setup.bat first.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo ERROR: Frontend not set up. Please run setup.bat first.
    pause
    exit /b 1
)

echo Starting Backend Server...
start "Smart Griev Backend" cmd /k "cd backend_django && venv\Scripts\activate && python manage.py runserver 0.0.0.0:8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...

REM Detect package manager
where pnpm >nul 2>&1
if %errorlevel% equ 0 (
    start "Smart Griev Frontend" cmd /k "pnpm dev"
) else (
    start "Smart Griev Frontend" cmd /k "npm run dev"
)

echo.
echo ================================
echo Servers are starting...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Admin Login:
echo   Email: admin@smartgriev.com
echo   Password: Admin@123
echo.
echo Press any key to stop all servers...
echo ================================
pause >nul

echo Stopping servers...
taskkill /FI "WindowTitle eq Smart Griev Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq Smart Griev Frontend*" /T /F >nul 2>&1
echo Servers stopped.
