"""Reporter base class for generating reports."""

from abc import ABC, abstractmethod


class Reporter(ABC):
    """Abstract base class for report generators."""

    @abstractmethod
    def generate(self, results: list, pattern_line_hits: dict, output_file: str, **kwargs):
        """
        Generate a report.
        
        Args:
            results: List of result dicts with pattern, status, paths
            pattern_line_hits: Dict mapping patterns to line hit details
            output_file: Path to output file
            **kwargs: Additional format-specific options
        """
        pass
