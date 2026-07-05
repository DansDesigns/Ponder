#!/usr/bin/env bash
# Ponder launcher for Linux
# Run with:  ./run.sh

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ -x "$DIR/venv/bin/python" ]; then
    PY="$DIR/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PY="python3"
    echo "  ⚠  No venv found at $DIR/venv — using system python3."
    echo "     Run ./install.sh first if you hit missing-dependency errors."
else
    echo "  ✗  No Python interpreter found. Run ./install.sh first." >&2
    exit 1
fi

exec "$PY" main.py "$@"
