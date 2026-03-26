"""CSV report generator."""

import csv
from .base import Reporter


class CsvReporter(Reporter):
    """Generate CSV reports."""

    def generate(self, results: list, pattern_line_hits: dict, output_file: str, **kwargs):
        """Generate a CSV report."""
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["pattern", "status", "paths"])
            for r in results:
                w.writerow([r["pattern"], r["status"], " | ".join(r["paths"])])
