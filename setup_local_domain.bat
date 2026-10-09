@echo off
title Configure Domain tnfarmerweathernoti.com
cls
echo ======================================================================
echo    CONFIGURING DOMAIN: http://tnfarmerweathernoti.com:8000
echo ======================================================================
echo.
echo Requesting administrator privileges to map tnfarmerweathernoti.com...
powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', 'Add-Content -Path \"$env:windir\System32\drivers\etc\hosts\" -Value \"`n127.0.0.1 tnfarmerweathernoti.com\"; Write-Host \"[OK] Domain tnfarmerweathernoti.com configured successfully!\" -ForegroundColor Green; Start-Sleep -Seconds 3'"
echo.
echo [DONE] Domain mapped to http://tnfarmerweathernoti.com:8000
pause
