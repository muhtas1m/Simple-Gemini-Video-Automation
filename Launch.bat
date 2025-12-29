@echo off
cd /d "%~dp0"
title Automation Studio
color 0B

:: --- UI HEADER ---
cls
echo.
echo  =======================================================
echo   AUTOMATION STUDIO
echo  =======================================================
echo.

:: --- STEP 1: SILENT INSTALL ---
echo  [+] Verifying core systems (Flask, Google GenAI)...
python -m pip install -q flask google-genai
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  [!] ERROR: Could not install libraries. Check Python installation.
    pause
    exit
)

:: --- STEP 2: OPEN BROWSER ---
echo  [+] Launching Interface...
:: Waits 3 seconds to let Python start, then opens browser
start "" "http://127.0.0.1:5000"

:: --- STEP 3: START SERVER ---
echo  [+] Server is live! 
echo      (Keep this window open while using the website)
echo.
echo  -------------------------------------------------------
python app.py
pause