@echo off
cd /d "%~dp0"
set PYTHON=C:\Users\mesen\anaconda3\python.exe
if not exist "%PYTHON%" set PYTHON=python

echo Stopping old server on port 5000 if any...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5000" ^| findstr "LISTENING"') do (
  taskkill /F /PID %%a >nul 2>&1
)

echo Fuzzy Exercise Assistant
echo.
echo Installing Flask...
"%PYTHON%" -m pip install flask -q
echo.
echo Starting server (keep this window open)...
echo.
echo   >>> Open: http://127.0.0.1:5000
echo   >>> Do NOT open index.html directly
echo.

start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

"%PYTHON%" server.py
if errorlevel 1 (
  echo.
  echo Server failed to start. See error above.
  pause
)
