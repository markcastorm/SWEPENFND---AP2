@echo off
REM Show scraper status
REM Double-click this file to view status

cd /d "%~dp0"

python orchestrator.py status

pause
