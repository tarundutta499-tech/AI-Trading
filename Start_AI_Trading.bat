@echo off
title AI Trading System
echo Starting AI Trading Backend...
cd "%~dp0backend"
start cmd /k "call venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000"

echo Starting AI Trading Frontend...
cd "%~dp0frontend"
start cmd /k "npm run dev -- --open"

echo.
echo The application is starting! 
echo A browser window will open automatically in a few seconds.
echo Please keep the black command prompt windows open while using the app.
pause
