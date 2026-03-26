"""
Run search-strings as a module: python -m search_strings
Also works when bundled as an executable with PyInstaller.
"""

import sys
import os

# Handle both module and executable contexts
try:
    # Try relative import (when run as a module)
    from .cli import main
except (ImportError, ValueError):
    # Fallback for PyInstaller bundled executables
    # Add the current directory to the path so absolute imports work
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        from search_strings.cli import main
    except ImportError:
        # Last resort: import cli directly
        from cli import main

if __name__ == "__main__":
    main()
