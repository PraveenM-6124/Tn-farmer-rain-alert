@echo off
:: Batch script to add tnfarmerweathernoti.com to Windows hosts file with Administrator elevation
echo Requesting administrator privileges to configure local domain...
powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile', '-Command', 'Add-Content -Path ''C:\Windows\System32\drivers\etc\hosts'' -Value \"`n127.0.0.1 tnfarmerweathernoti.com\"; Write-Host \"Domain tnfarmerweathernoti.com added successfully!\"; Start-Sleep -Seconds 2'"
echo Done! You can now open http://tnfarmerweathernoti.com:8000 in your browser.
pause
