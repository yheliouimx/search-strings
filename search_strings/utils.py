"""
Utility functions for search-strings.
"""

import subprocess
import shutil
from rich.console import Console

# Global debug flag
DEBUG_ENABLED = False


def set_debug(enabled: bool):
    """Enable or disable debug mode."""
    global DEBUG_ENABLED
    DEBUG_ENABLED = enabled


def debug(msg: str):
    """Print debug message if DEBUG_ENABLED."""
    if DEBUG_ENABLED:
        print(f"[DEBUG] {msg}")


def normalize_path(path: str) -> str:
    """Normalize path separators to forward slashes."""
    return path.replace("\\", "/")


def run_cmd(cmd):
    """Execute a shell command and return output."""
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return out.decode("utf-8", "ignore").strip()
    except Exception:
        return ""


def check_ripgrep() -> bool:
    """Check if ripgrep (rg) is installed."""
    return shutil.which("rg") is not None


def propose_install_ripgrep():
    """Propose ripgrep installation with platform-specific instructions."""
    console = Console()
    console.print("[red]ripgrep (rg) is not installed.[/red]")

    ans = input("Show installation instructions? [Y/n]: ").strip().lower()
    if ans not in ("", "y", "yes"):
        return

    import platform
    osname = platform.system()

    console.print("[cyan]Install ripgrep using the commands below:[/cyan]\n")

    if osname == "Windows":
        console.print("""
Windows:
  winget install BurntSushi.ripgrep
  choco install ripgrep
  scoop install ripgrep
""")
    elif osname == "Linux":
        console.print("""
Linux:
  Ubuntu/Debian: sudo apt install ripgrep
  Fedora: sudo dnf install ripgrep
  Arch: sudo pacman -S ripgrep
""")
    elif osname == "Darwin":
        console.print("macOS:\n  brew install ripgrep")
    else:
        console.print("Install manually: https://github.com/BurntSushi/ripgrep")
