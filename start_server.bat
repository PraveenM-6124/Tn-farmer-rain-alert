@echo off
title Tamil Nadu Farmer Rain Alert Server
cls
echo ======================================================================
echo    FARMER RAIN ALERT ^& MARKETPLACE (TAMIL NADU)
echo ======================================================================
echo.
echo  Website URL: http://tnfarmerweathernoti.com:8000
echo.
echo  Press Ctrl+C to stop the server anytime.
echo ======================================================================
echo.

:: Automatically open browser on tnfarmerweathernoti.com
start "" "http://tnfarmerweathernoti.com:8000"

:: Start Uvicorn server
.\.venv\Scripts\uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
