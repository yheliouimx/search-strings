"""Grep-based fallback searcher."""

import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base import Searcher


class GrepSearcher(Searcher):
    """Fallback searcher using grep."""

    def search(self, patterns: list, files: list = None, threads: int = None, **kwargs) -> tuple:
        """
        Search for patterns using grep (parallel).
        
        Args:
            patterns: List of patterns to search for
            files: List of file paths to search
            threads: Number of threads to use
            **kwargs: Unused
        
        Returns:
            (pattern_map, empty_line_hits) - grep fallback doesn't track line details
        """
        if not files:
            return defaultdict(set), defaultdict(list)

        if threads is None:
            import os
            threads = os.cpu_count()

        pat_map = defaultdict(set)

        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(self._grep_file, patterns, f): f for f in files}

            for fut in as_completed(futures):
                f = futures[fut]
                try:
                    matches = fut.result()
                    for p in matches:
                        pat_map[p].add(f)
                except Exception:
                    pass

        return pat_map, defaultdict(list)

    @staticmethod
    def _grep_file(patterns: list, filepath: str) -> list:
        """Grep a single file for patterns."""
        found = []
        for p in patterns:
            cmd = ["grep", "-R", "-s", "-n", "-F", p, filepath]
            if (
                subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                == 0
            ):
                found.append(p)
        return found
