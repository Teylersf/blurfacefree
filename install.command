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
  - From https://www.python.org/downloads/  (recommended)
  - Or via Homebrew:  brew install python

EOF
  read -n 1 -s -r -p "Press any key to close."
  exit 1
fi

echo "Using: $($PY --version)  -> $(which $PY)"
echo

echo "=== Step 1/2: Upgrading pip ==="
$PY -m pip install --upgrade pip --user || $PY -m pip install --upgrade pip

echo
echo "=== Step 2/2: Installing face-blur engine + GUI dependencies ==="
$PY -m pip install -r requirements.txt --user || $PY -m pip install -r requirements.txt

echo
echo "==========================================================="
echo " Install complete!"
echo
echo " Next step: double-click  'Blur Faces.command'  to open the app."
echo "==========================================================="
echo
read -n 1 -s -r -p "Press any key to close."
