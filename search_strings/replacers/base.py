"""Abstract base class for replacers."""

from abc import ABC, abstractmethod


class Replacer(ABC):
    """Abstract base class for string replacers."""

    @abstractmethod
    def replace(self, pairs: list, files: list, dry_run: bool = True) -> list:
        """
        Replace patterns in files.

        Args:
            pairs: List of (old_string, new_string) tuples
            files: List of file paths to process
            dry_run: If True, compute changes but don't write

        Returns:
            List of change dicts:
            [{
                "file": str,
                "line": int,
                "old": str,
                "new": str,
                "content_before": str,
                "content_after": str,
                "applied": bool
            }]
        """
        pass
