@echo off
setlocal

set SCRIPT=%~1
for %%I in ("%SCRIPT%") do set SCRIPT_NAME=%%~nxI

:: Check if script is already running
tasklist /FI "IMAGENAME eq AutoHotkey64.exe" /V | findstr /I "%SCRIPT_NAME%" >nul

if %errorlevel%==0 (
    echo Script is running. Killing...

    powershell -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'AutoHotkey64.exe' -and $_.CommandLine -like '*%SCRIPT_NAME%*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
) else (
    echo Script not running. Launching...
    start "" "dir\AutoHotkey64.exe" "%SCRIPT%"
)

exit /b