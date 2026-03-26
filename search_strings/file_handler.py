"""
File system operations for search-strings.
"""

import os
from .utils import normalize_path


def list_files(directory: str, extensions: set = None) -> list:
    """
    Recursively list all files in directory.
    
    Args:
        directory: Root directory to scan
        extensions: Set of allowed extensions (None = all files)
    
    Returns:
        List of normalized file paths
    """
    result = []
    for root, _, files in os.walk(directory):
        for f in files:
            ext = f.split(".")[-1].lower() if "." in f else ""
            if extensions and ext not in extensions:
                continue
            result.append(normalize_path(os.path.join(root, f)))
    return result
