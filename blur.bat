@echo off
REM Drag a video file (or several) onto this .bat to blur faces.
REM Output is saved next to the input with "_anonymized" suffix, audio kept.

setlocal

if "%~1"=="" (
  echo Usage: drag one or more video files onto this .bat
  echo    or: blur.bat path\to\video.mp4
  pause
  exit /b 1
)

:loop
if "%~1"=="" goto done
echo.
echo === Blurring: %~1 ===
python -m deface --keep-audio --thresh 0.2 "%~1"
shift
goto loop

:done
echo.
echo All done. Look for *_anonymized.mp4 next to each input.
pause
