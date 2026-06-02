#!/usr/bin/env bash
# compile_and_preview.sh — run a matplotlib script and verify output.png exists.
#
# Usage:   ./compile_and_preview.sh path/to/chart.py
# Output:  prints "✓ output.png  (WxH, D dpi)" on success, traceback on failure.
#
# Exits 0 if the script ran and produced output.png, 1 otherwise.
#
# Optional env:
#   MPLBACKEND  - matplotlib backend (default: Agg, headless).
#   PYTHON      - python interpreter (default: python3).

set -uo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 path/to/chart.py" >&2
  exit 2
fi

script="$1"
if [[ ! -f "$script" ]]; then
  echo "✗ file not found: $script" >&2
  exit 1
fi

script_dir="$(cd "$(dirname "$script")" && pwd)"
script_name="$(basename "$script")"
work_dir="$(mktemp -d -t image-to-chart-XXXXXX)"
trap 'rm -rf "$work_dir"' EXIT

cp "$script" "$work_dir/chart.py"

# Headless backend — required for sandbox / no-display environments.
export MPLBACKEND="${MPLBACKEND:-Agg}"
py="${PYTHON:-python3}"

cd "$work_dir"

echo "[1/1]  $py $script_name"
if ! "$py" chart.py; then
  echo "✗ script failed — see traceback above" >&2
  exit 1
fi

if [[ ! -f output.png ]]; then
  echo "✗ script exited 0 but output.png was not produced" >&2
  echo "  (your script must end with plt.savefig('output.png', ...))" >&2
  exit 1
fi

# Warn if the script used plt.show() (which blocks in headless mode).
if grep -qE 'plt\.show\(\s*\)' chart.py; then
  echo "  warning: plt.show() detected — replace with plt.savefig(...)" >&2
fi

# Print file size and dimensions for quick sanity.
if command -v sips >/dev/null 2>&1; then
  dims=$(sips -g pixelWidth -g pixelHeight output.png 2>/dev/null \
         | awk '/pixelW/ {w=$2} /pixelH/ {h=$2} END {print w"x"h}')
  echo "✓ output.png  ($dims, 200 dpi)"
elif command -v identify >/dev/null 2>&1; then
  dims=$(identify -format '%wx%h' output.png 2>/dev/null)
  echo "✓ output.png  ($dims, 200 dpi)"
else
  bytes=$(wc -c < output.png | tr -d ' ')
  echo "✓ output.png  ($bytes bytes)"
fi

# Copy the rendered PNG next to the source script so the user can find it.
cp output.png "$script_dir/output.png"
echo "  saved next to source: $script_dir/output.png"
