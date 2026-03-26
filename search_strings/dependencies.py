"""
Dependency management for search-strings.
"""

import os
import sys
import subprocess
from .config import REQUIRED_MODULES


def ensure_dependencies(auto_yes=False):
    """Install missing Python dependencies automatically."""
    missing = []
    for mod in REQUIRED_MODULES:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)

    if not missing:
        return

    print("\n🔧 Missing Python modules:", ", ".join(missing))
    if not auto_yes:
        ans = input("Install them now? [Y/n] ").strip().lower()
        if ans not in ("", "y", "yes"):
            print("❌ Cannot continue.")
            sys.exit(1)

    print("\n📦 Installing modules...")
    for m in missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", m])

    print("✅ Dependencies installed. Restarting script...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


def safe_import():
    """Safely import all required modules after ensuring they're installed."""
    import tqdm
    from colorama import Fore, Style, init as colorama_init
    import pandas
    import openpyxl
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text

    colorama_init()
    return tqdm, Fore, Style, pandas, openpyxl, Console, Table, Panel, Text
