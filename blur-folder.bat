@echo off
REM Blurs every video in .\input and writes results to .\output
REM Keeps audio. Uses GPU via DirectML if available.

setlocal
set "HERE=%~dp0"

if not exist "%HERE%input" (
  echo No 'input' folder found next to this script.
  pause
  exit /b 1
)

for %%F in ("%HERE%input\*.mp4" "%HERE%input\*.mov" "%HERE%input\*.mkv" "%HERE%input\*.avi" "%HERE%input\*.webm") do (
  if exist "%%~F" (
    echo.
    echo === Blurring: %%~nxF ===
    python -m deface --keep-audio --thresh 0.2 -o "%HERE%output\%%~nF_anonymized%%~xF" "%%~F"
  )
)

echo.
echo Done. Results in: %HERE%output
pause
