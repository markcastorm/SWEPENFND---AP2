@echo off
REM Installation script for AP2 Scraper
REM Double-click this file to install dependencies

echo ========================================
echo AP2 Scraper - Installation
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Installation failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Running configuration test...
echo.

python test_config.py

echo.
echo You can now run the scraper:
echo   - Double-click run.bat
echo   - Or run: python orchestrator.py run
echo.

pause
