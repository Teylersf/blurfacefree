@echo off
REM Launches the drag-and-drop GUI. Double-click this file.
REM If pythonw isn't found, falls back to python (shows console).
where pythonw >nul 2>&1
if errorlevel 1 (
  start "" python "%~dp0blur_gui.pyw"
) else (
  start "" pythonw "%~dp0blur_gui.pyw"
)
