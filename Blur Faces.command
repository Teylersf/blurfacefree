#!/bin/bash
# Launches the drag-and-drop GUI on macOS.
cd "$(dirname "$0")"
if command -v pythonw >/dev/null 2>&1; then
  pythonw blur_gui.pyw &
else
  python3 blur_gui.pyw &
fi
disown 2>/dev/null || true
sleep 0.4
exit 0
