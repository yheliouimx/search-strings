"""JSON report generator."""

import json
from .base import Reporter


class JsonReporter(Reporter):
    """Generate JSON reports."""

    def generate(self, results: list, pattern_line_hits: dict, output_file: str, **kwargs):
        """Generate a JSON report."""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
