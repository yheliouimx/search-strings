#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
search-strings.py - Command-line wrapper

This is a simple entry point that imports and runs the search_strings package.
The actual implementation is in the search_strings/ package for better modularity.

For development or direct execution:
    python search-strings.py patterns.txt /path/to/search --excel

For installation as a package:
    pip install .
    search-strings patterns.txt /path/to/search --excel

For execution as module:
    python -m search_strings patterns.txt /path/to/search --excel
"""

import sys

try:
    from search_strings.cli import main
except ImportError:
    print("Error: search_strings package not found.")
    print("Please ensure the search_strings package is in the same directory or installed.")
    sys.exit(1)


if __name__ == "__main__":
    main()
