"""Launch blur_gui, screenshot its window, close it. Used for README image."""
import subprocess
import sys
import time
from pathlib import Path

import win32con
import win32gui
from PIL import ImageGrab

ROOT = Path(__file__).resolve().parent.parent
GUI = ROOT / "blur_gui.pyw"
OUT = ROOT / "docs" / "screenshot.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

TITLE = "Blur Faces - local + free (deface)"

proc = subprocess.Popen(["pythonw", str(GUI)])
print(f"Launched pythonw PID {proc.pid}")

hwnd = 0
for _ in range(40):
    time.sleep(0.25)
    hwnd = win32gui.FindWindow(None, TITLE)
    if hwnd:
        break

if not hwnd:
    print("ERROR: window not found")
    proc.kill()
    sys.exit(1)

print(f"Found HWND {hwnd}")
try:
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
except Exception:
    pass
try:
    win32gui.SetForegroundWindow(hwnd)
except Exception:
    pass
time.sleep(0.8)

rect = win32gui.GetWindowRect(hwnd)
print(f"Window rect: {rect}")

img = ImageGrab.grab(bbox=rect, all_screens=True)
img.save(OUT)
print(f"Saved: {OUT}  size={img.size}")

try:
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
except Exception:
    pass
time.sleep(0.5)
if proc.poll() is None:
    proc.kill()
