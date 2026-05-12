@echo off
REM One-click installer for Blur Faces Free
REM Run this once after extracting the ZIP.

title Installing Blur Faces Free...
setlocal

where python >nul 2>&1
if errorlevel 1 (
  echo.
  echo [X] Python is not installed (or not on PATH^).
  echo.
  echo Please install Python 3.10 or newer:
  echo    1. Download from https://www.python.org/downloads/
  echo    2. During install, CHECK the box "Add Python to PATH"
  echo    3. Re-run this installer.
  echo.
  pause
  exit /b 1
)

echo.
echo === Step 1/2: Upgrading pip ===
python -m pip install --upgrade pip
if errorlevel 1 goto fail

echo.
echo === Step 2/2: Installing face-blur engine + GUI dependencies ===
python -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto fail

echo.
echo ===========================================================
echo  Install complete!
echo.
echo  Next step:  double-click  "Blur Faces.bat"  to open the app.
echo ===========================================================
echo.
pause
exit /b 0

:fail
echo.
echo [X] Install failed. Scroll up and check the error message.
echo Common fixes:
echo   - Make sure you're connected to the internet.
echo   - Try right-clicking this file and "Run as administrator".
pause
exit /b 1
