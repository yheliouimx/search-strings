"""Main orchestration logic for search-strings."""

import os
from collections import defaultdict
from .file_handler import list_files
from .utils import check_ripgrep, propose_install_ripgrep, debug
from .searchers import FilenameSearcher, RipgrepSearcher, GrepSearcher
from .replacers import FileReplacer
from .ui import rich_summary, rich_details
from .reporters import HtmlReporter, ExcelReporter, JsonReporter, CsvReporter
from .reporters import (
    ReplaceHtmlReporter, ReplaceExcelReporter,
    ReplaceJsonReporter, ReplaceCsvReporter,
)


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

    def run_replace(self, pairs: list, directory: str, extensions: set = None,
                    threads: int = None, use_rg: bool = True,
                    dry_run: bool = True, backup: bool = False,
                    quiet: bool = False) -> dict:
        """
        Execute the replace workflow.

        Uses ripgrep to find candidate files, then replaces in-memory
        (dry-run) or on disk.

        Args:
            pairs: List of (old_string, new_string) tuples
            directory: Root directory to search
            extensions: Extension filter set
            threads: Thread count (unused for now, reserved)
            use_rg: Use ripgrep for file discovery
            dry_run: If True, preview only
            backup: If True, create .bak before writing
            quiet: Suppress console output

        Returns:
            dict with keys: changes, skipped, files_scanned, files_modified
        """
        if threads is None:
            threads = os.cpu_count()

        # List files
        if not quiet:
            self.console.print("[yellow]Scanning filesystem...[/yellow]")

        files = list_files(directory, extensions)

        if not files:
            self.console.print("[red]No files match extension filter.[/red]")
            return {"changes": [], "skipped": [], "files_scanned": 0,
                    "files_modified": 0}

        if not quiet:
            self.console.print(f"[green]Found {len(files)} files[/green]\n")

        # Use ripgrep to narrow down candidate files
        candidate_files = files
        used_rg = False
        if use_rg and check_ripgrep():
            if not quiet:
                self.console.print("[green]Using ripgrep to find candidates...[/green]")
            candidate_files = self._find_candidates_rg(pairs, directory)
            used_rg = True
            # Filter by extensions if rg returned paths outside filter
            if extensions:
                candidate_files = [
                    f for f in candidate_files
                    if f.rsplit(".", 1)[-1].lower() in extensions
                ]
            if not quiet:
                self.console.print(
                    f"[green]{len(candidate_files)} files contain matches[/green]\n"
                )

        if not candidate_files:
            if not quiet:
                self.console.print("[yellow]No files contain matching patterns.[/yellow]")
            return {"changes": [], "skipped": [], "files_scanned": len(files),
                    "files_modified": 0}

        # Replace
        replacer = FileReplacer()
        changes, skipped = replacer.replace(
            pairs, candidate_files, dry_run=dry_run, backup=backup,
            rg_validated=used_rg
        )

        # Display results
        if not quiet:
            self._display_replace_preview(changes, dry_run)
            self._display_replace_summary(changes, skipped, len(files), dry_run)

        return {
            "changes": changes,
            "skipped": skipped,
            "files_scanned": len(files),
            "files_modified": len({c["file"] for c in changes if c["applied"]}),
        }

    def _find_candidates_rg(self, pairs: list, directory: str) -> list:
        """Use ripgrep -l to quickly find files containing any old pattern."""
        from .utils import run_cmd, normalize_path

        # Resolve directory to absolute path so rg output paths are absolute
        abs_directory = os.path.abspath(directory)

        candidates = set()
        for old, _ in pairs:
            cmd = ["rg", "--fixed-strings", "--color", "never", "-l", old,
                   abs_directory]
            debug(f"rg candidate search: {' '.join(cmd)}")
            out = run_cmd(cmd)
            if out:
                for line in out.splitlines():
                    line = line.strip()
                    if line:
                        candidates.add(normalize_path(os.path.abspath(line)))
        return sorted(candidates)

    def _display_replace_preview(self, changes: list, dry_run: bool):
        """Show a diff-style preview of all changes."""

        if not changes:
            self.console.print("[yellow]No replacements to show.[/yellow]")
            return

        title = "DRY RUN -- No files modified" if dry_run else "Replacements Applied"
        style = "yellow" if dry_run else "green"

        separator = "-" * 80
        self.console.print()
        self.console.print(f"[bold {style}]{separator}[/bold {style}]")
        self.console.print(f"[bold {style}]  {title}[/bold {style}]")
        self.console.print(f"[bold {style}]{separator}[/bold {style}]")
        self.console.print()

        for c in changes:
            self.console.print(f"[cyan]{c['file']}[/cyan]")
            self.console.print(f"  Line {c['line']}")
            self.console.print(f"  [red]--- {c['content_before']}[/red]")
            self.console.print(f"  [green]+++ {c['content_after']}[/green]")
            self.console.print()

        self.console.print(f"[bold {style}]{separator}[/bold {style}]")

    def _display_replace_summary(self, changes: list, skipped: list,
                                  files_scanned: int, dry_run: bool):
        """Show a plain-text summary of the replace operation."""
        from collections import Counter

        files_affected = len({c["file"] for c in changes})
        total = len(changes)

        # Per-pair breakdown
        pair_counts = Counter()
        for c in changes:
            pair_counts[(c["old"], c["new"])] += 1

        action = "would be modified" if dry_run else "modified"
        title_style = "yellow" if dry_run else "green"
        title_text = "Dry Run Summary" if dry_run else "Replace Summary"

        sep = "=" * 50
        self.console.print()
        self.console.print(f"[bold {title_style}]{sep}[/bold {title_style}]")
        self.console.print(f"[bold {title_style}]  {title_text}[/bold {title_style}]")
        self.console.print(f"[bold {title_style}]{sep}[/bold {title_style}]")
        self.console.print(f"  Files scanned:      {files_scanned}")
        self.console.print(f"  Files {action}:  {files_affected}")
        self.console.print(f"  Total replacements: {total}")

        if skipped:
            self.console.print(f"  Files skipped:      {len(skipped)}")

        self.console.print()
        self.console.print("  Pairs:")
        for (old, new), count in pair_counts.items():
            new_display = new if new else "(empty -- deletion)"
            self.console.print(f"    {old} -> {new_display}  ({count} matches)")

        self.console.print(f"[bold {title_style}]{sep}[/bold {title_style}]")

    def generate_replace_reports(self, changes: list, skipped: list,
                                  files_scanned: int, dry_run: bool, prefix: str,
                                  html: bool = False, excel: bool = False,
                                  json: bool = False, csv: bool = False,
                                  quiet: bool = False):
        """Generate reports for replace operations."""
        if html:
            reporter = ReplaceHtmlReporter()
            html_file = f"{prefix}.html"
            reporter.generate(changes, skipped, files_scanned, dry_run, html_file)
            if not quiet:
                self.console.print(f"[green]Saved HTML ->[/green] {html_file}")

        if excel:
            reporter = ReplaceExcelReporter()
            excel_file = f"{prefix}.xlsx"
            reporter.generate(changes, skipped, files_scanned, dry_run,
                              excel_file, pandas=self.pandas, openpyxl=self.openpyxl)
            if not quiet:
                self.console.print(f"[green]Saved XLSX ->[/green] {excel_file}")

        if json:
            reporter = ReplaceJsonReporter()
            json_file = f"{prefix}.json"
            reporter.generate(changes, skipped, files_scanned, dry_run, json_file)
            if not quiet:
                self.console.print(f"[green]Saved JSON ->[/green] {json_file}")

        if csv:
            reporter = ReplaceCsvReporter()
            csv_file = f"{prefix}.csv"
            reporter.generate(changes, skipped, files_scanned, dry_run, csv_file)
            if not quiet:
                self.console.print(f"[green]Saved CSV  ->[/green] {csv_file}")
