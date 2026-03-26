"""Filename pattern searcher."""

import os
from collections import defaultdict
from .base import Searcher


class FilenameSearcher(Searcher):
    """Search for patterns in filenames."""

    def search(self, patterns: list, files: list = None, **kwargs) -> tuple:
        """
        Search for patterns in filenames.
        
        Args:
            patterns: List of patterns to search for
            files: List of file paths
            **kwargs: Unused
        
        Returns:
            (pattern_map, empty_line_hits) - filenames don't have line numbers
        """
        if not files:
            return defaultdict(set), defaultdict(list)

        pat_map = defaultdict(set)
        for f in files:
            name = os.path.basename(f).lower()
            for p in patterns:
                if p.lower() in name:
                    pat_map[p].add(f)
        
        return pat_map, defaultdict(list)
