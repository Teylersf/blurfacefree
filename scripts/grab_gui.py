"""Launch blur_gui, screenshot its window (even if obscured), close it."""
import ctypes
import subprocess
import sys
import time
from pathlib import Path

import win32con
import win32gui
import win32ui
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
GUI = ROOT / "blur_gui.pyw"
OUT = ROOT / "docs" / "screenshot.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

TITLE = "blur faces - free, local, no cap"

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

# Give the window a moment to fully render
time.sleep(1.0)

left, top, right, bottom = win32gui.GetWindowRect(hwnd)
w, h = right - left, bottom - top
print(f"Window rect: {(left, top, right, bottom)}  size=({w}, {h})")

# PrintWindow with PW_RENDERFULLCONTENT (0x2) grabs the actual window pixels,
# regardless of z-order or occlusion.
hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()
bmp = win32ui.CreateBitmap()
bmp.CreateCompatibleBitmap(mfcDC, w, h)
saveDC.SelectObject(bmp)

result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
print(f"PrintWindow result: {result}")

info = bmp.GetInfo()
bits = bmp.GetBitmapBits(True)
img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]),
                       bits, "raw", "BGRX", 0, 1)

win32gui.DeleteObject(bmp.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)

img.save(OUT)
print(f"Saved: {OUT}  size={img.size}")

try:
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
except Exception:
    pass
time.sleep(0.5)
if proc.poll() is None:
    proc.kill()
