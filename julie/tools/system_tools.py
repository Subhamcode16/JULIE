"""System action utilities for Julie."""

import os
import re
import subprocess
from pathlib import Path
from typing import Any

import winreg

try:
    from core.security import is_path_blocked
except ImportError:
    from julie.core.security import is_path_blocked


# Common app name aliases -> their Windows executable/shell names
_APP_ALIASES: dict[str, str] = {
    # Browsers
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "mozilla firefox": "firefox",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "brave": "brave",
    # Media
    "spotify": "spotify",
    "vlc": "vlc",
    "media player": "wmplayer",
    "windows media player": "wmplayer",
    # Dev
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "notepad": "notepad",
    "notepad++": "notepad++",
    "terminal": "wt",
    "windows terminal": "wt",
    "powershell": "powershell",
    "cmd": "cmd",
    "command prompt": "cmd",
    # Apps
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "ms paint": "mspaint",
    "word": "winword",
    "microsoft word": "winword",
    "excel": "excel",
    "microsoft excel": "excel",
    "outlook": "outlook",
    "microsoft outlook": "outlook",
    "teams": "teams",
    "microsoft teams": "teams",
    "discord": "discord",
    "slack": "slack",
    "zoom": "zoom",
    "obs": "obs64",
    "obs studio": "obs64",
    "steam": "steam",
    "file explorer": "explorer",
    "explorer": "explorer",
    "task manager": "taskmgr",
    "taskmgr": "taskmgr",
}


def _normalize_app_name(name: str) -> str:
    """Normalize a spoken app name before lookup."""
    # Strip trailing filler and punctuation like "for me?", "please!"
    name = re.sub(r"\s+(?:for me|please|now|right now|quickly)[.?!]?$", "", name, flags=re.IGNORECASE)
    # Also strip any trailing punctuation (?, !, .)
    name = re.sub(r"[.?!]+$", "", name)
    return name.strip().lower()


def find_executable(name: str) -> str | None:
    """Find executable in PATH."""
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(folder) / name
        if candidate.exists():
            return str(candidate)
    return None


def resolve_app_path(app_name: str) -> str | None:
    """Resolve a Windows application executable path by common name."""
    normalized = _normalize_app_name(app_name)

    # 1. Check alias map first
    exe_name = _APP_ALIASES.get(normalized)
    if exe_name:
        path = find_executable(exe_name) or find_executable(f"{exe_name}.exe")
        if path:
            return path
        # Return alias anyway — Windows shell / Start-Process can find it
        return exe_name

    # 2. Try candidates based on raw name
    candidates = [app_name, f"{app_name}.exe", app_name.replace(" ", ""), app_name.replace(" ", "-")]
    for candidate in candidates:
        path = find_executable(candidate)
        if path:
            return path

    # 3. Registry lookup
    for hive, root in (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
    ):
        for candidate in [app_name, normalized]:
            try:
                with winreg.OpenKey(hive, f"{root}\\{candidate}.exe") as key:
                    value, _ = winreg.QueryValueEx(key, None)
                    if Path(value).exists():
                        return value
            except FileNotFoundError:
                continue

    return None


def launch_application(executable: str, args: list[str] | None = None) -> dict[str, Any]:
    """Launch the given application executable.
    
    Falls back to Windows Start-Process via PowerShell if direct Popen fails,
    which handles UWP apps, Store apps, and shell-registered apps.
    """
    if args is None:
        args = []

    command = [executable] + args
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {
            "success": True,
            "pid": proc.pid,
            "command": command,
        }
    except Exception:
        pass

    # Fallback: use PowerShell Start-Process (handles UWP, shell commands, ms- URIs)
    try:
        ps_command = ["powershell", "-NoProfile", "-Command", f"Start-Process '{executable}'"]
        proc = subprocess.Popen(ps_command)
        return {
            "success": True,
            "pid": proc.pid,
            "command": ps_command,
            "method": "powershell_fallback",
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "command": command,
        }


def run_terminal_command(command: str, cwd: str | None = None, timeout: int = 30) -> dict[str, Any]:
    """Run a terminal command and capture output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "success": False,
            "error": "timeout",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }


def read_file(path: str) -> dict[str, Any]:
    """Read text content from a file."""
    try:
        if is_path_blocked(path):
            return {"success": False, "error": f"Blocked path: {path}"}
        content = Path(path).read_text(encoding="utf-8")
        return {"success": True, "content": content}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def write_file(path: str, content: str) -> dict[str, Any]:
    """Write text content to a file."""
    try:
        if is_path_blocked(path):
            return {"success": False, "error": f"Blocked path: {path}"}
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"success": True, "path": str(target)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def list_directory(path: str) -> dict[str, Any]:
    """List files and directories."""
    try:
        if is_path_blocked(path):
            return {"success": False, "error": f"Blocked path: {path}"}
        items = [p.name for p in Path(path).iterdir()]
        return {"success": True, "items": items}
    except Exception as exc:
        return {"success": False, "error": str(exc)}
