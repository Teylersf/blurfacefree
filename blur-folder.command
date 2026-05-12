#!/bin/bash
# Blurs every video in ./input and writes results to ./output (macOS).
cd "$(dirname "$0")"

if [ ! -d "input" ]; then
  echo "No 'input' folder found next to this script."
  read -n 1 -s -r -p "Press any key to close."
  exit 1
fi

mkdir -p output
shopt -s nullglob
for f in input/*.mp4 input/*.mov input/*.mkv input/*.avi input/*.webm input/*.m4v; do
  base="$(basename "$f")"
  name="${base%.*}"
  ext="${base##*.}"
  echo
  echo "=== Blurring: $base ==="
  python3 -m deface --keep-audio --thresh 0.2 \
    -o "output/${name}_anonymized.${ext}" "$f"
done

echo
echo "Done. Results in: $(pwd)/output"
read -n 1 -s -r -p "Press any key to close."
