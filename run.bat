@echo off
REM Quick run script for AP2 Scraper
REM Double-click this file to run the scraper

echo ========================================
echo AP2 Financial Reports Scraper
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Starting scraper...
echo.

python orchestrator.py run --retry

echo.
echo ========================================
echo Scraper finished
echo ========================================
echo.
echo Results saved to: output\latest\
echo.

pause
