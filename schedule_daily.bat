@echo off
REM Schedule the scraper to run daily at 9:00 AM
REM Double-click this file to start daily scheduled runs

echo ========================================
echo AP2 Scraper - Daily Schedule
echo ========================================
echo.
echo This will run the scraper every day at 9:00 AM
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"

python orchestrator.py daily --hour 9 --minute 0

pause
