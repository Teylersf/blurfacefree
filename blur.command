#!/bin/bash
# Blur one or more videos from the command line. Usage:
#   ./blur.command path/to/video.mp4 [more.mp4 ...]

cd "$(dirname "$0")"

if [ "$#" -eq 0 ]; then
  echo "Usage: ./blur.command path/to/video.mp4 [more.mp4 ...]"
  read -n 1 -s -r -p "Press any key to close."
  exit 1
fi

for f in "$@"; do
  echo
  echo "=== Blurring: $f ==="
  python3 -m deface --keep-audio --thresh 0.2 "$f"
done

echo
echo "All done. Look for *_anonymized.mp4 next to each input."
read -n 1 -s -r -p "Press any key to close."
