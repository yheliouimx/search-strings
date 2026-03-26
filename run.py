"""
PyInstaller-friendly entry point for search-strings.

This file is designed to be used with PyInstaller to create standalone executables:
    pyinstaller --onefile run.py --name search-strings

It handles imports gracefully whether run as a module or as a bundled executable.
"""

import sys
import os

# Ensure the search_strings package can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import and run the CLI
if __name__ == "__main__":
    try:
        from search_strings.cli import main
    except ImportError as e:
        print(f"Error: Could not import search_strings.cli - {e}")
        print("Make sure the search_strings package is in the same directory as this script.")
        sys.exit(1)
    
    main()
