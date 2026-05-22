@echo off
cd /d "%~dp0"
set PYTHON=C:\Users\mesen\anaconda3\python.exe
if not exist "%PYTHON%" set PYTHON=python

echo Installing fcmpy WITHOUT old pandas (uses your current pandas 2.x)...
echo.
"%PYTHON%" -m pip install fcmpy --no-deps -q
"%PYTHON%" -m pip install scikit-fuzzy -q
echo.
"%PYTHON%" -c "from fcmpy import FcmSimulator; print('fcmpy is ready.')"
if errorlevel 1 (
  echo fcmpy import failed. The app still works with the built-in FCM engine.
  pause
  exit /b 1
)
echo.
echo Done. Restart START.bat to use the fcmpy library.
pause
