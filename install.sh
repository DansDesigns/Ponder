#!/usr/bin/env bash
# Ponder installer for Linux
# Run with:  ./install.sh   (or  bash install.sh)

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

say()  { printf "  %s\n" "$1"; }
ok()   { printf "  \xE2\x9C\x93  %s\n" "$1"; }
info() { printf "  \xE2\x84\xB9  %s\n" "$1"; }
err()  { printf "  \xE2\x9C\x97  %s\n" "$1" >&2; exit 1; }

echo
echo "  ┌──────────────────────────────────────┐"
echo "  │           Ponder  installer           │"
echo "  │           Linux                       │"
echo "  └──────────────────────────────────────┘"
say

# ── Find Python ─────────────────────────────────────────────────────────
PY=""
for cand in python3 python; do
    if command -v "$cand" >/dev/null 2>&1; then
        PY="$cand"
        break
    fi
done

if [ -z "$PY" ]; then
    err "Python not found. Install it with: sudo apt install python3 python3-venv"
fi

PY_VER=$("$PY" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    err "Python 3.10+ required — you have $PY_VER. Try: sudo apt install python3.11"
fi
ok "Python $PY_VER"

# ── Virtualenv ───────────────────────────────────────────────────────────
if [ ! -d "$DIR/venv" ]; then
    say "Creating virtualenv…"
    "$PY" -m venv venv || err "venv creation failed — try: sudo apt install python3-venv"
fi

VENV_PY="$DIR/venv/bin/python"

say "Installing dependencies…"
"$VENV_PY" -m pip install --quiet --upgrade pip
if [ -f "$DIR/requirements.txt" ]; then
    "$VENV_PY" -m pip install --quiet -r "$DIR/requirements.txt"
else
    err "requirements.txt not found in $DIR"
fi
ok "Dependencies installed"

# ── static/index.html placement ──────────────────────────────────────────
mkdir -p "$DIR/static"
if [ -f "$DIR/index.html" ] && [ ! -f "$DIR/static/index.html" ]; then
    mv "$DIR/index.html" "$DIR/static/index.html"
    ok "Moved index.html → static/index.html"
elif [ ! -f "$DIR/static/index.html" ]; then
    err "index.html not found. Expected: $DIR/static/index.html or $DIR/index.html"
fi

# ── run.sh permissions ────────────────────────────────────────────────────
chmod +x "$DIR/run.sh" 2>/dev/null || true

# ── CLI launcher ──────────────────────────────────────────────────────────
echo
echo "  ── Linux shortcuts ──────────────────────"

LAUNCHER_BODY="#!/usr/bin/env bash
cd \"$DIR\"
exec \"$VENV_PY\" main.py \"\$@\"
"

if [ -w /usr/local/bin ] || [ "$(id -u)" -eq 0 ]; then
    printf '%s' "$LAUNCHER_BODY" > /usr/local/bin/ponder 2>/dev/null && \
        chmod +x /usr/local/bin/ponder && \
        ok "CLI launcher: /usr/local/bin/ponder" || {
            mkdir -p "$HOME/.local/bin"
            printf '%s' "$LAUNCHER_BODY" > "$HOME/.local/bin/ponder"
            chmod +x "$HOME/.local/bin/ponder"
            ok "CLI launcher: $HOME/.local/bin/ponder  (add ~/.local/bin to PATH if needed)"
        }
else
    mkdir -p "$HOME/.local/bin"
    printf '%s' "$LAUNCHER_BODY" > "$HOME/.local/bin/ponder"
    chmod +x "$HOME/.local/bin/ponder"
    ok "CLI launcher: $HOME/.local/bin/ponder  (add ~/.local/bin to PATH if needed)"
fi

# ── .desktop entry ────────────────────────────────────────────────────────
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"
DESKTOP_FILE="$APPS_DIR/ponder.desktop"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Ponder
GenericName=Search
Comment=Local-first search — web, files and wiki
Exec=bash -c "cd \"$DIR\" && \"$VENV_PY\" main.py"
Icon=$DIR/logo.png
Terminal=true
Categories=Network;Search;Utility;
Keywords=search;web;files;wiki;
EOF
chmod +x "$DESKTOP_FILE"
ok "App menu entry: $DESKTOP_FILE"

if [ -d "$HOME/Desktop" ]; then
    cp "$DESKTOP_FILE" "$HOME/Desktop/Ponder.desktop"
    chmod +x "$HOME/Desktop/Ponder.desktop"
    ok "Desktop shortcut: $HOME/Desktop/Ponder.desktop"
fi

# ── hosts file (127.0.0.1  ponder) ───────────────────────────────────────
echo
echo "  ── Browser address ──────────────────────"
if grep -q "ponder" /etc/hosts 2>/dev/null; then
    ok "hosts file: 'ponder' already present"
else
    ENTRY="127.0.0.1  ponder  # Ponder local search"
    if [ -w /etc/hosts ]; then
        echo "$ENTRY" >> /etc/hosts
        ok "hosts file: 'ponder' → 127.0.0.1"
    elif command -v sudo >/dev/null 2>&1; then
        if sudo bash -c "echo '$ENTRY' >> /etc/hosts" 2>/dev/null; then
            ok "hosts file: 'ponder' → 127.0.0.1"
        else
            info "hosts file: couldn't write — add manually to /etc/hosts:"
            info "  127.0.0.1  ponder"
        fi
    else
        info "hosts file: couldn't write — add manually to /etc/hosts:"
        info "  127.0.0.1  ponder"
    fi
fi

echo
echo "  ┌──────────────────────────────────────────┐"
echo "  │  Done!                                    │"
echo "  │  Start:  ./run.sh   or   ponder            │"
echo "  │                                            │"
echo "  │  Browser (any of these work):             │"
echo "  │    http://localhost:7000                  │"
echo "  │    http://ponder:7000  (after hosts setup)│"
echo "  │                                            │"
echo "  │  Config: ~/.config/ponder/config.json     │"
echo "  └──────────────────────────────────────────┘"
echo
