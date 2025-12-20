@echo off
echo ==========================================
echo    Smart Grievance - Push to GitHub
echo ==========================================
echo.
echo Pushing code to https://github.com/rajashekhar1977/smart-griev.git...
echo You may be asked for your GitHub username and password (or PAT).
echo.

git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ==========================================
    echo Push Failed!
    echo Please check your internet connection or GitHub credentials.
    echo You may need to sign in via the popup or use a Personal Access Token.
    echo ==========================================
    pause
    exit /b
)

echo.
echo ==========================================
echo       Code Pushed Successfully!
echo ==========================================
echo.
pause
