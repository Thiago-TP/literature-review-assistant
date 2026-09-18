#!/bin/sh
# Convenience wrapper for macOS/Linux. The launcher itself is run.py, which
# is shared with Windows so there is only one copy of the start-up logic.
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python 3 not found on PATH. Install Python 3.13+ and try again." >&2
  exit 1
fi

exec "$PYTHON" "$ROOT_DIR/run.py" "$@"
