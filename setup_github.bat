@echo off
echo ========================================
echo    Event Manager - GitHub Setup Script
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo.
    echo Please install Git first:
    echo 1. Go to: https://git-scm.com/download/win
    echo 2. Download and install Git
    echo 3. Restart this script
    echo.
    pause
    exit /b 1
)

echo Git is installed! ✓
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    echo ERROR: manage.py not found!
    echo Please run this script from your Event Manager project directory.
    echo.
    pause
    exit /b 1
)

echo Project directory found! ✓
echo.

REM Initialize Git repository
echo Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize Git repository
    pause
    exit /b 1
)

echo Git repository initialized! ✓
echo.

REM Add all files
echo Adding files to Git...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)

echo Files added to Git! ✓
echo.

REM Create initial commit
echo Creating initial commit...
git commit -m "Initial commit: Complete Event Manager Platform with AI features"
if %errorlevel% neq 0 (
    echo ERROR: Failed to create commit
    pause
    exit /b 1
)

echo Initial commit created! ✓
echo.

echo ========================================
echo           SETUP COMPLETE! ✓
echo ========================================
echo.
echo Next steps:
echo 1. Go to GitHub.com and create a new repository
echo 2. Copy the repository URL
echo 3. Run these commands:
echo.
echo    git remote add origin YOUR_REPOSITORY_URL
echo    git push -u origin main
echo.
echo 4. Follow the LinkedIn setup guide in LINKEDIN_CONTENT.md
echo.
echo Your project is now ready for GitHub! 🚀
echo.
pause
