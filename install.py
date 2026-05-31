#!/usr/bin/env python3
"""
Ponder installer — works on Linux, macOS, and Windows.
Run with:  python install.py
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

PONDER_DIR = Path(__file__).parent.resolve()
OS = platform.system()  # 'Linux' | 'Darwin' | 'Windows'


# ── Helpers ───────────────────────────────────────────────────────────────

def say(msg=""):
    print(f"  {msg}")

def ok(msg):
    print(f"  ✓  {msg}")

def info(msg):
    print(f"  ℹ  {msg}")

def err(msg):
    print(f"  ✗  {msg}")
    sys.exit(1)

def banner(title):
    print(f"\n  ── {title} {'─' * max(0, 38 - len(title))}")


# ── Python version check ──────────────────────────────────────────────────

def check_python():
    v = sys.version_info
    if v.major < 3 or v.minor < 10:
        hints = {
            "Linux":   "sudo apt install python3   or   https://python.org",
            "Darwin":  "brew install python3        or   https://python.org",
            "Windows": "https://python.org/downloads  (tick 'Add to PATH')",
        }
        err(
            f"Python 3.10+ required — you have {v.major}.{v.minor}.\n"
            f"     {hints.get(OS, 'https://python.org')}"
        )
    ok(f"Python {v.major}.{v.minor}.{v.micro}")


# ── Virtualenv + dependencies ─────────────────────────────────────────────

def setup_venv():
    venv = PONDER_DIR / "venv"
    if not venv.exists():
        say("Creating virtualenv…")
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)

    scripts = "Scripts" if OS == "Windows" else "bin"
    python = venv / scripts / ("python.exe" if OS == "Windows" else "python")

    say("Installing dependencies…")
    if OS != "Windows":
        subprocess.run(
            [str(python), "-m", "pip", "install", "--quiet", "--upgrade", "pip"],
            check=True,
        )
    subprocess.run(
        [str(python), "-m", "pip", "install", "--quiet",
         "-r", str(PONDER_DIR / "requirements.txt")],
        check=True,
    )
    ok("Dependencies installed")

    # Ensure static/ folder exists and index.html is inside it
    static_dir = PONDER_DIR / "static"
    static_dir.mkdir(exist_ok=True)
    loose_html = PONDER_DIR / "index.html"
    target_html = static_dir / "index.html"
    if loose_html.exists() and not target_html.exists():
        shutil.move(str(loose_html), str(target_html))
        ok(f"Moved index.html → static/index.html")
    elif not target_html.exists():
        err(
            "index.html not found.\n"
            f"     Expected: {target_html}\n"
            f"     Or:       {loose_html}\n"
            f"     Download index.html from the Ponder repo and place it in: {PONDER_DIR}"
        )

    return python


# ── Hosts file ────────────────────────────────────────────────────────────

HOSTS_ENTRY = "127.0.0.1  ponder"

def _hosts_has_entry() -> bool:
    hosts = _hosts_path()
    try:
        return "ponder" in hosts.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

def _hosts_path() -> Path:
    if OS == "Windows":
        return Path(r"C:\Windows\System32\drivers\etc\hosts")
    return Path("/etc/hosts")

def add_hosts_entry():
    """Add '127.0.0.1  ponder' to the system hosts file."""
    if _hosts_has_entry():
        ok("hosts file: 'ponder' already present")
        return

    hosts = _hosts_path()
    entry = f"\n{HOSTS_ENTRY}  # Ponder local search\n"

    if OS == "Windows":
        # Write via PowerShell (needs elevation — silently skips if denied)
        ps_cmd = (
            f'Add-Content -Path "{hosts}" -Value "{HOSTS_ENTRY}  # Ponder local search"'
            f' -Encoding UTF8'
        )
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
        )
        if r.returncode == 0:
            ok(f"hosts file: 'ponder' → 127.0.0.1")
        else:
            info("hosts file: needs admin — run install.py as Administrator to add 'ponder'")
            info(f"Or manually add to {hosts}:  {HOSTS_ENTRY}")
    else:
        try:
            # Try direct write first (works if running as root)
            with open(hosts, "a") as f:
                f.write(entry)
            ok(f"hosts file: 'ponder' → 127.0.0.1")
        except PermissionError:
            try:
                subprocess.run(
                    ["sudo", "bash", "-c", f'echo "{HOSTS_ENTRY}  # Ponder" >> {hosts}'],
                    check=True,
                )
                ok(f"hosts file: 'ponder' → 127.0.0.1")
            except Exception:
                info(f"hosts file: couldn't write — add manually to {hosts}:")
                info(f"  {HOSTS_ENTRY}")


# ── Linux shortcuts ───────────────────────────────────────────────────────

def install_linux(python):
    banner("Linux shortcuts")

    venv_python = str(python)

    # 1. CLI launcher
    bin_path = Path("/usr/local/bin/ponder")
    launcher = f'#!/usr/bin/env bash\ncd "{PONDER_DIR}"\nexec "{venv_python}" main.py "$@"\n'
    try:
        bin_path.write_text(launcher)
        bin_path.chmod(0o755)
        ok(f"CLI launcher: {bin_path}")
    except PermissionError:
        local_bin = Path.home() / ".local" / "bin"
        local_bin.mkdir(parents=True, exist_ok=True)
        alt = local_bin / "ponder"
        alt.write_text(launcher)
        alt.chmod(0o755)
        ok(f"CLI launcher: {alt}  (add ~/.local/bin to PATH if needed)")

    # 2. .desktop entry (app menu)
    apps_dir = Path.home() / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    desktop = apps_dir / "ponder.desktop"
    desktop.write_text(
        f"[Desktop Entry]\n"
        f"Version=1.0\n"
        f"Type=Application\n"
        f"Name=Ponder\n"
        f"GenericName=Search\n"
        f"Comment=Local-first search — web, files and wiki\n"
        f'Exec=bash -c "cd \\"{PONDER_DIR}\\" && \\"{venv_python}\\" main.py"\n'
        f"Icon={PONDER_DIR / 'logo.png'}\n"
        f"Terminal=true\n"
        f"Categories=Network;Search;Utility;\n"
        f"Keywords=search;web;files;wiki;\n"
    )
    desktop.chmod(0o755)
    ok(f"App menu entry: {desktop}")

    # 3. Desktop shortcut
    desk = Path.home() / "Desktop"
    if desk.is_dir():
        shortcut = desk / "Ponder.desktop"
        shutil.copy(desktop, shortcut)
        shortcut.chmod(0o755)
        ok(f"Desktop shortcut: {shortcut}")


# ── macOS shortcuts ───────────────────────────────────────────────────────

def install_mac(python):
    banner("macOS shortcuts")

    venv_python = str(python)

    # 1. CLI launcher
    for bin_dir in [Path("/usr/local/bin"), Path.home() / ".local" / "bin"]:
        try:
            bin_dir.mkdir(parents=True, exist_ok=True)
            launcher_path = bin_dir / "ponder"
            launcher_path.write_text(
                f'#!/usr/bin/env bash\ncd "{PONDER_DIR}"\nexec "{venv_python}" main.py "$@"\n'
            )
            launcher_path.chmod(0o755)
            ok(f"CLI launcher: {launcher_path}")
            if bin_dir == Path.home() / ".local" / "bin":
                info('Add to PATH: export PATH="$HOME/.local/bin:$PATH"')
            break
        except PermissionError:
            continue

    # 2. Double-clickable .command on Desktop
    desk = Path.home() / "Desktop"
    desk.mkdir(exist_ok=True)
    cmd_file = desk / "Ponder.command"
    cmd_file.write_text(
        f'#!/usr/bin/env bash\ncd "{PONDER_DIR}"\n"{venv_python}" main.py\n'
    )
    cmd_file.chmod(0o755)
    ok(f"Desktop launcher: {cmd_file}  (double-click to run)")

    # 3. Minimal .app bundle
    apps = Path.home() / "Applications"
    apps.mkdir(exist_ok=True)
    app = apps / "Ponder.app" / "Contents"
    (app / "MacOS").mkdir(parents=True, exist_ok=True)

    exe = app / "MacOS" / "Ponder"
    exe.write_text(f'#!/usr/bin/env bash\nopen -a Terminal "{cmd_file}"\n')
    exe.chmod(0o755)

    (app / "Info.plist").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"'
        ' "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        "<plist version=\"1.0\"><dict>\n"
        "  <key>CFBundleName</key>        <string>Ponder</string>\n"
        "  <key>CFBundleExecutable</key>  <string>Ponder</string>\n"
        "  <key>CFBundleIdentifier</key>  <string>com.dansdesigns.ponder</string>\n"
        "  <key>CFBundleVersion</key>     <string>1.0</string>\n"
        "  <key>CFBundlePackageType</key> <string>APPL</string>\n"
        "</dict></plist>\n"
    )
    ok(f"App bundle: ~/Applications/Ponder.app  (drag to Dock)")


# ── Windows helpers ───────────────────────────────────────────────────────

def _find_desktop_windows():
    """Return the real Desktop path — handles OneDrive-moved desktops."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        )
        desk, _ = winreg.QueryValueEx(key, "Desktop")
        winreg.CloseKey(key)
        p = Path(desk)
        if p.exists():
            return p
    except Exception:
        pass
    for candidate in [
        Path.home() / "Desktop",
        Path.home() / "OneDrive" / "Desktop",
        Path(os.environ.get("USERPROFILE", "")) / "Desktop",
    ]:
        if candidate.exists():
            return candidate
    return Path.home() / "Desktop"


def _find_start_menu_windows():
    """Return the user's Start Menu > Programs folder."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        )
        sm, _ = winreg.QueryValueEx(key, "Programs")
        winreg.CloseKey(key)
        return Path(sm)
    except Exception:
        pass
    return (
        Path(os.environ.get("APPDATA", ""))
        / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    )


def _make_lnk(lnk, target, args=""):
    """Create a .lnk shortcut with Ponder icon and optional arguments."""
    ico       = PONDER_DIR / "ponder.ico"
    icon_line = f'$s.IconLocation="{ico},0";' if ico.exists() else ''
    args_line = f'$s.Arguments="{args}";' if args else ''
    ps = (
        f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{lnk}");'
        f'$s.TargetPath="{target}";'
        f'{args_line}'
        f'$s.WorkingDirectory="{PONDER_DIR}";'
        f'$s.Description="Ponder - local-first search";'
        f'{icon_line}'
        f'$s.WindowStyle=1;$s.Save()'
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True)
    return r.returncode == 0


def _make_lnk_bat(lnk, bat):
    """Explicit bat variant — same as _make_lnk for clarity."""
    return _make_lnk(lnk, bat)


def _make_lnk_vbs(lnk, vbs):
    """VBS variant: routes through wscript.exe so the window is truly hidden."""
    ps = (
        f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{lnk}");'
        f'$s.TargetPath="wscript.exe";'
        f'$s.Arguments=\'"{vbs}"\';'
        f'$s.WorkingDirectory="{PONDER_DIR}";'
        f'$s.Description="Ponder - local-first search (silent)";'
        f'$s.WindowStyle=7;$s.Save()'
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True)
    return r.returncode == 0


def _add_to_path_windows(directory):
    """Add directory to the user's persistent PATH via the registry."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0, winreg.KEY_READ | winreg.KEY_WRITE,
        )
        try:
            current, reg_type = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current, reg_type = "", winreg.REG_EXPAND_SZ

        parts = [p for p in current.split(";") if p.strip()]
        if directory.lower() in [p.lower() for p in parts]:
            winreg.CloseKey(key)
            return False  # already present

        parts.append(directory)
        winreg.SetValueEx(key, "Path", 0, reg_type, ";".join(parts))
        winreg.CloseKey(key)

        # Broadcast change so open terminals pick it up without a reboot
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(
            0xFFFF, 0x001A, 0, "Environment", 2, 5000, None
        )
        return True
    except Exception as e:
        info(f"PATH registry update skipped ({e})")
        return False


# ── Windows install ───────────────────────────────────────────────────────

def install_windows(python):
    banner("Windows shortcuts")

    venv_python = str(python)
    dir_str     = str(PONDER_DIR)

    say(f"Project location: {dir_str}")

    # 1. ponder.bat — visible console, useful for debugging
    bat = PONDER_DIR / "ponder.bat"
    bat.write_text(
        f'@echo off\r\n'
        f'cd /d "{dir_str}"\r\n'
        f'"{venv_python}" main.py %*\r\n'
    )
    ok(f"Batch launcher:  {bat}")

    # 1b. ponder_silent.vbs — runs ponder.bat with no visible CMD window
    vbs = PONDER_DIR / "ponder_silent.vbs"
    vbs.write_text(
        f'Set ws = CreateObject("WScript.Shell")\r\n'
        f'ws.Run Chr(34) & "{bat}" & Chr(34), 0, False\r\n'
        f'Set ws = Nothing\r\n'
    )
    ok(f"Silent launcher: {vbs}")

    # 4. Regenerate Ponder.lnk in project dir (silent, with icon)
    #    This is the canonical shortcut — copy it anywhere you like
    wscript  = Path(os.environ.get("SystemRoot", "C:\\Windows")) / "System32" / "wscript.exe"
    lnk_proj = PONDER_DIR / "Ponder.lnk"
    _make_lnk(lnk_proj, str(wscript), args=str(vbs))
    ok(f"Project shortcut:          {lnk_proj}  (silent, no CMD window)")

    # Copy to Desktop
    desktop = _find_desktop_windows()
    desktop.mkdir(parents=True, exist_ok=True)
    lnk_desk = desktop / "Ponder.lnk"
    try:
        import shutil
        shutil.copy2(lnk_proj, lnk_desk)
        ok(f"Desktop shortcut:          {lnk_desk}")
    except Exception as e:
        info(f"Desktop shortcut skipped ({e})")

    # Copy to Start Menu
    start_menu = _find_start_menu_windows()
    start_menu.mkdir(parents=True, exist_ok=True)
    lnk_sm = start_menu / "Ponder.lnk"
    try:
        shutil.copy2(lnk_proj, lnk_sm)
        ok(f"Start Menu shortcut:       {lnk_sm}")
    except Exception as e:
        info(f"Start Menu shortcut skipped ({e})")

    # 5. Add project dir to user PATH
    say()
    say("Updating user PATH…")
    if _add_to_path_windows(dir_str):
        ok(f"PATH updated  →  'ponder' works in any new terminal")
        info("Open a new CMD or PowerShell window for this to take effect")
    else:
        info("Already in PATH — no change needed")

    # 6. Hosts file
    banner("Browser address")
    add_hosts_entry()

    # 7. Port 80 → 7000 proxy (one-time, needs admin — makes http://ponder work)
    banner("Port forwarding  (http://ponder without :7000)")
    _setup_port_proxy_windows()


def _setup_port_proxy_windows():
    """Forward port 80 → 7000 so http://ponder works without typing a port."""
    # Check if already set up
    check = subprocess.run(
        ["netsh", "interface", "portproxy", "show", "v4tov4"],
        capture_output=True, text=True,
    )
    if ":7000" in check.stdout:
        ok("Port proxy already configured  →  http://ponder works")
        return
    r = subprocess.run(
        ["netsh", "interface", "portproxy", "add", "v4tov4",
         "listenaddress=127.0.0.1", "listenport=80",
         "connectaddress=127.0.0.1", "connectport=7000"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        ok("Port proxy set  →  http://ponder now works in any browser")
        info("(This setting persists across reboots)")
    else:
        info("Port proxy needs admin — run install.py as Administrator to enable")
        info("Or type:  http://ponder:7000  (the port is only needed without admin setup)")


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    print()
    print("  ┌──────────────────────────────────────┐")
    print("  │           Ponder  installer           │")
    print(f"  │           {OS:<29}│")
    print("  └──────────────────────────────────────┘")
    say()

    check_python()
    python = setup_venv()

    match OS:
        case "Linux":
            install_linux(python)
            banner("Browser address")
            add_hosts_entry()
        case "Darwin":
            install_mac(python)
            banner("Browser address")
            add_hosts_entry()
        case "Windows":
            install_windows(python)   # hosts entry called inside
        case _:
            info(f"Unknown OS '{OS}' — skipping shortcuts.")
            info(f"Run manually:  python main.py")

    print()
    print("  ┌──────────────────────────────────────────┐")
    print("  │  Done!                                    │")
    if OS == "Windows":
        print("  │  Start:           ponder.bat                │")
        print("  │  Start (visible): ponder.bat             │")
        print("  │  Log file:        ponder.log             │")
    else:
        print("  │  Start:  ponder                          │")
    print("  │                                           │")
    print("  │  Browser (any of these work):            │")
    print("  │    http://localhost:7000                  │")
    print("  │    http://ponder.localhost:7000           │")
    print("  │    http://ponder:7000  (after hosts setup)│")
    print("  │                                           │")
    print("  │  Config: ~/.config/ponder/config.json    │")
    print("  └──────────────────────────────────────────┘")
    print()


if __name__ == "__main__":
    main()
