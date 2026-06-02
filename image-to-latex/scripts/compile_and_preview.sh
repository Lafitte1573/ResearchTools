#!/bin/bash
# compile_and_preview.sh — compile a .tex file and render the result as PNG
#
# Usage:
#   compile_and_preview.sh <file.tex> [--engine pdflatex|xelatex|lualatex] [--height N]
#
# Behavior:
#   - Runs the chosen engine in nonstop mode.
#   - On success, converts the PDF to a PNG via sips (macOS) or pdftoppm (Linux).
#   - Prints the absolute paths of the produced PDF and PNG.
#   - On failure, prints the last meaningful error block from the .log file.
#
# Auto-detects the engine:
#   - If the source loads `ctex`, `fontspec`, or `unicode-math` → switch to xelatex.
#   - Override with --engine.

set -u

FILE=""
ENGINE=""
HEIGHT=2000

while [[ $# -gt 0 ]]; do
  case "$1" in
    --engine) ENGINE="$2"; shift 2 ;;
    --height) HEIGHT="$2"; shift 2 ;;
    -h|--help)
      sed -n '2,16p' "$0"; exit 0 ;;
    *) FILE="$1"; shift ;;
  esac
done

if [[ -z "$FILE" ]]; then
  echo "error: no .tex file given" >&2
  echo "usage: $0 <file.tex> [--engine ...] [--height N]" >&2
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo "error: file not found: $FILE" >&2
  exit 1
fi

# resolve to absolute path
FILE_ABS=$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")
DIR=$(dirname "$FILE_ABS")
STEM=$(basename "$FILE" .tex)

# auto-detect engine
if [[ -z "$ENGINE" ]]; then
  if grep -qE '\\usepackage(\[[^]]*\])?\{(ctex|fontspec|unicode-math)\}' "$FILE_ABS"; then
    ENGINE="xelatex"
  else
    ENGINE="pdflatex"
  fi
fi

if ! command -v "$ENGINE" >/dev/null 2>&1; then
  echo "error: $ENGINE not found in PATH" >&2
  echo "       install TeX Live or MacTeX to get it" >&2
  exit 1
fi

cd "$DIR"

# compile (twice if it looks like there are references)
"$ENGINE" -interaction=nonstopmode -halt-on-error "$STEM.tex" > /tmp/compile_output.txt 2>&1
STATUS=$?

if [[ $STATUS -ne 0 ]]; then
  echo "=== COMPILATION FAILED ===" >&2
  # surface the most useful section of the log
  if [[ -f "$STEM.log" ]]; then
    # find the first "!" error and show 10 lines after it
    grep -n -A 10 -m 3 '^!' "$STEM.log" >&2 || tail -40 "$STEM.log" >&2
  else
    tail -40 /tmp/compile_output.txt >&2
  fi
  exit 1
fi

# convert PDF → PNG
PDF="$DIR/$STEM.pdf"
PNG="$DIR/$STEM.png"

if [[ ! -f "$PDF" ]]; then
  echo "error: $PDF not produced even though $ENGINE returned 0" >&2
  exit 1
fi

if command -v sips >/dev/null 2>&1; then
  # macOS
  sips -s format png --resampleHeight "$HEIGHT" "$PDF" --out "$PNG" > /dev/null 2>&1
elif command -v pdftoppm >/dev/null 2>&1; then
  # Linux
  pdftoppm -png -r 200 "$PDF" "$DIR/$STEM" > /dev/null 2>&1
  # pdftoppm appends a page number suffix; normalize the filename
  [[ -f "$DIR/$STEM-1.png" ]] && mv "$DIR/$STEM-1.png" "$PNG"
else
  echo "warning: neither sips nor pdftoppm found; skipping PNG render" >&2
  PNG=""
fi

# success report
echo "OK"
echo "engine: $ENGINE"
echo "pdf:    $PDF"
[[ -n "$PNG" && -f "$PNG" ]] && echo "png:    $PNG"
