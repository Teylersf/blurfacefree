#!/bin/bash
# One-click installer for Blur Faces Free (macOS).
# Double-click this file. If macOS refuses, see: README.md "First-time Mac launch"

set -e
cd "$(dirname "$0")"
echo "=== Blur Faces Free — macOS installer ==="
echo

# Locate Python 3
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1 && python -c 'import sys; sys.exit(0 if sys.version_info[0]==3 else 1)'; then
  PY=python
else
  cat <<'EOF'
[X] Python 3 is not installed.

Install one of these (then re-run this file):
  - From https://www.python.org/downloads/  (recommended — bundles Tk)
  - Or via Homebrew:  brew install python python-tk

EOF
  read -n 1 -s -r -p "Press any key to close."
  exit 1
fi

echo "Using: $($PY --version)  ->  $(which $PY)"
echo

echo "=== Step 1/3: Upgrading pip ==="
$PY -m pip install --upgrade pip --user || $PY -m pip install --upgrade pip

echo
echo "=== Step 2/3: Installing face-blur engine + GUI dependencies ==="
$PY -m pip install -r requirements.txt --user || $PY -m pip install -r requirements.txt

echo
echo "=== Step 3/3: Sanity check (Tk + tkinterdnd2 + deface) ==="
if $PY -c "import tkinter, tkinterdnd2, deface" 2>/tmp/blurfacefree_check.err; then
  echo "All good."
else
  echo
  echo "[!] Install finished but a required module failed to import:"
  cat /tmp/blurfacefree_check.err
  rm -f /tmp/blurfacefree_check.err
  echo
  echo "Most common cause: Homebrew Python ships WITHOUT Tk by default."
  echo "Fix one of these ways:"
  echo "  1. Install Python from https://www.python.org/downloads/ (recommended)"
  echo "  2. Or:  brew install python-tk@3.13   (match your Python minor version)"
  echo
  read -n 1 -s -r -p "Press any key to close."
  exit 1
fi
rm -f /tmp/blurfacefree_check.err

echo
echo "==========================================================="
echo " Install complete!"
echo
echo " Next step: double-click  'Blur Faces.command'  to open the app."
echo "==========================================================="
echo
read -n 1 -s -r -p "Press any key to close."
