"""Searcher classes for pattern matching."""

from abc import ABC, abstractmethod
from collections import defaultdict


class Searcher(ABC):
    """Abstract base class for pattern searchers."""

    @abstractmethod
    def search(self, patterns: list, files: list = None, **kwargs) -> tuple:
        """
        Search for patterns.
        
        Returns:
            (pattern_map, pattern_line_hits)
            - pattern_map: dict {pattern: set of file paths}
            - pattern_line_hits: dict {pattern: list of line hit dicts}
        """
        pass
