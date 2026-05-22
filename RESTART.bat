@echo off
cd /d "%~dp0"
set PYTHON=C:\Users\mesen\anaconda3\python.exe
if not exist "%PYTHON%" set PYTHON=python

echo ============================================
echo   Fuzzy Exercise Assistant - RESTART
echo ============================================
echo.
echo Stopping ALL old servers on port 5000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
  echo   Stopping PID %%a
  taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul
echo.
echo Starting NEW server (BMI 10-60, not slider 1-10)...
echo.
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"
"%PYTHON%" server.py
pause
