"""
search-strings - High-performance recursive pattern search tool

Features:
- ripgrep primary engine (multi-threaded)
- grep fallback with ThreadPoolExecutor
- filename + content scanning
- extension filtering
- progress bars
- HTML / Excel / JSON / CSV reporting
- pretty terminal output via Rich
- auto dependency installation
"""

__version__ = "2.0.0"
__author__ = "Youssef HELIOUI"

from .cli import main
from .orchestrator import SearchOrchestrator

__all__ = ["main", "SearchOrchestrator"]
