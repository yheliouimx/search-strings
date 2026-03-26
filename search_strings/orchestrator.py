"""Main orchestration logic for search-strings."""

import os
from collections import defaultdict
from .file_handler import list_files
from .utils import check_ripgrep, propose_install_ripgrep, debug
from .searchers import FilenameSearcher, RipgrepSearcher, GrepSearcher
from .ui import rich_summary, rich_details
from .reporters import HtmlReporter, ExcelReporter, JsonReporter, CsvReporter


class SearchOrchestrator:
    """Orchestrates the entire search workflow."""

    def __init__(self, console, pandas=None, openpyxl=None):
        """
        Initialize orchestrator.
        
        Args:
            console: Rich Console instance for output
            pandas: pandas module (required for Excel reports)
            openpyxl: openpyxl module (required for Excel reports)
        """
        self.console = console
        self.pandas = pandas
        self.openpyxl = openpyxl

    def run(self, patterns: list, directory: str, patterns_file: str = None, 
            extensions: set = None, threads: int = None, use_rg: bool = True,
            quiet: bool = False) -> dict:
        """
        Execute the search workflow.
        
        Returns:
            dict with keys: results, pattern_line_hits, files_count
        """
        if threads is None:
            threads = os.cpu_count()

        # List files
        if not quiet:
            self.console.print("[yellow]Scanning filesystem...[/yellow]")

        files = list_files(directory, extensions)

        if not files:
            self.console.print("[red]No files match extension filter.[/red]")
            return {"results": [], "pattern_line_hits": defaultdict(list), "files_count": 0}

        if not quiet:
            self.console.print(f"[green]Found {len(files)} files[/green]\n")

        # Search
        pattern_line_hits = defaultdict(list)
        filename_map = defaultdict(set)

        # Filename search
        filename_searcher = FilenameSearcher()
        fname_map, _ = filename_searcher.search(patterns, files)
        filename_map.update(fname_map)

        # Content search
        if use_rg and check_ripgrep():
            if not quiet:
                self.console.print("[green]Using ripgrep[/green]")
            rg_searcher = RipgrepSearcher()
            rg_map, rg_line_hits = rg_searcher.search(
                patterns, files, patterns_file, directory
            )
            filename_map.update(rg_map)
            for p, entries in rg_line_hits.items():
                pattern_line_hits[p].extend(entries)
        else:
            if not check_ripgrep():
                propose_install_ripgrep()
            if not quiet:
                self.console.print("[red]ripgrep unavailable → grep fallback[/red]")
            grep_searcher = GrepSearcher()
            grep_map, _ = grep_searcher.search(patterns, files, threads)
            filename_map.update(grep_map)

        # Build results
        results = []
        for p in patterns:
            paths = sorted(filename_map[p])
            status = "FOUND" if paths else "MISSING"
            results.append({"pattern": p, "status": status, "paths": paths})

        # Display UI
        if not quiet:
            from .ui import rich_summary, rich_details
            from rich.table import Table
            from rich.panel import Panel
            from rich.text import Text
            
            rich_summary(results, type(self.console), Table, Text)
            self.console.print()
            rich_details(results, type(self.console), Panel, Text)

        return {
            "results": results,
            "pattern_line_hits": pattern_line_hits,
            "files_count": len(files)
        }

    def generate_reports(self, results: list, pattern_line_hits: dict, prefix: str,
                        html: bool = False, excel: bool = False, 
                        json: bool = False, csv: bool = False, quiet: bool = False):
        """
        Generate output reports.
        
        Args:
            results: List of result dicts
            pattern_line_hits: Dict of line hit details
            prefix: Output file prefix (without extension)
            html: Generate HTML report
            excel: Generate Excel report
            json: Generate JSON report
            csv: Generate CSV report
            quiet: Suppress console output
        """
        if html:
            reporter = HtmlReporter()
            html_file = f"{prefix}.html"
            reporter.generate(results, pattern_line_hits, html_file)
            if not quiet:
                self.console.print(f"[green]Saved HTML →[/green] {html_file}")

        if excel:
            reporter = ExcelReporter()
            excel_file = f"{prefix}.xlsx"
            reporter.generate(results, pattern_line_hits, excel_file, 
                            pandas=self.pandas, openpyxl=self.openpyxl)
            if not quiet:
                self.console.print(f"[green]Saved XLSX →[/green] {excel_file}")

        if json:
            reporter = JsonReporter()
            json_file = f"{prefix}.json"
            reporter.generate(results, pattern_line_hits, json_file)
            if not quiet:
                self.console.print(f"[green]Saved JSON →[/green] {json_file}")

        if csv:
            reporter = CsvReporter()
            csv_file = f"{prefix}.csv"
            reporter.generate(results, pattern_line_hits, csv_file)
            if not quiet:
                self.console.print(f"[green]Saved CSV  →[/green] {csv_file}")

        if not quiet and (html or excel or json or csv):
            self.console.print("\n[green]All reports generated successfully.[/green]\n")
