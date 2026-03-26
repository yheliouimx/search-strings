"""Command-line interface for search-strings."""

import os
import sys
import argparse
from datetime import datetime
from .dependencies import ensure_dependencies, safe_import
from .utils import set_debug
from .orchestrator import SearchOrchestrator


def load_replacement_pairs(filepath: str):
    """
    Load replacement pairs from file.
    Each line: old_string|new_string
    Use ``\\|`` to include a literal pipe in the strings.

    Returns:
        List of (old, new) tuples
    """
    pairs = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, 1):
            line = raw_line.strip()
            if not line:
                continue
            # Split on unescaped pipes: split on | but not \|
            # Replace escaped pipes with a placeholder, split, restore
            placeholder = "\x00PIPE\x00"
            safe = line.replace("\\|", placeholder)
            parts = safe.split("|")
            if len(parts) != 2:
                raise ValueError(
                    f"Line {line_num}: expected 'old|new', got: {line}"
                )
            old = parts[0].replace(placeholder, "|").strip()
            new = parts[1].replace(placeholder, "|").strip()
            if not old:
                raise ValueError(
                    f"Line {line_num}: old string cannot be empty"
                )
            pairs.append((old, new))
    return pairs


def load_patterns(patterns_arg: str):
    """
    Load patterns from file or treat as single pattern.
    
    Returns:
        (patterns_list, patterns_file_path)
    """
    if "--single" in sys.argv or os.path.isfile(patterns_arg):
        patterns_file = patterns_arg if os.path.isfile(patterns_arg) else ""
        if patterns_file:
            with open(patterns_file, "r", encoding="utf-8") as f:
                patterns = [x.strip() for x in f if x.strip()]
        else:
            patterns = [patterns_arg.strip()]
        return patterns, patterns_file

    # Try as file first, then as single pattern
    if os.path.isfile(patterns_arg):
        with open(patterns_arg, "r", encoding="utf-8") as f:
            patterns = [x.strip() for x in f if x.strip()]
        return patterns, patterns_arg
    else:
        return [patterns_arg.strip()], ""


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="search-strings - High-performance pattern scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for patterns in a file
  search-strings patterns.txt /path/to/search --excel --html
  
  # Search for a single pattern
  search-strings "search_term" /path/to/search --single --all-reports
  
  # Filter by extensions
  search-strings patterns.txt . --extensions xml,txt,json
        """
    )
    
    parser.add_argument("patterns", 
                       help="File containing patterns (one per line) or single pattern")
    parser.add_argument("directory", 
                       help="Directory to search recursively")
    parser.add_argument("--single", action="store_true",
                       help="Treat first argument as literal pattern instead of file")
    parser.add_argument("--extensions", default="",
                       help="Comma-separated file extensions to filter (e.g., xml,txt,json)")
    parser.add_argument("--threads", type=int, default=os.cpu_count(),
                       help=f"Number of threads for grep fallback (default: {os.cpu_count()})")
    parser.add_argument("--html", action="store_true",
                       help="Generate HTML report")
    parser.add_argument("--excel", action="store_true",
                       help="Generate Excel report")
    parser.add_argument("--csv", action="store_true",
                       help="Generate CSV report")
    parser.add_argument("--json", action="store_true",
                       help="Generate JSON report")
    parser.add_argument("--all-reports", action="store_true",
                       help="Generate all report formats")
    parser.add_argument("--no-rg", action="store_true",
                       help="Force grep fallback (don't use ripgrep)")
    parser.add_argument("--quiet", action="store_true",
                       help="Suppress console output")
    parser.add_argument("--yes", action="store_true",
                       help="Auto-install missing dependencies without asking")
    parser.add_argument("--debug", action="store_true",
                       help="Enable detailed debug logs")

    # Replace mode options
    replace_group = parser.add_argument_group("Replace mode")
    replace_group.add_argument("--replace", metavar="NEW_STRING", default=None,
                              help="Replace matched pattern with NEW_STRING (use with --single)")
    replace_group.add_argument("--replace-strings", action="store_true",
                              help="Treat patterns file as replacement pairs (old|new per line)")
    replace_group.add_argument("--dry-run", action="store_true",
                              help="Preview replacements without modifying files")
    replace_group.add_argument("--backup", action="store_true",
                              help="Create .bak copies before replacing")

    args = parser.parse_args()

    # Setup
    set_debug(args.debug)
    ensure_dependencies(auto_yes=args.yes)
    tqdm, Fore, Style, pandas, openpyxl, Console, Table, Panel, Text = safe_import()

    console = Console()

    if args.debug:
        console.print("[yellow]DEBUG MODE ENABLED[/yellow]")

    # Load patterns
    if args.single:
        patterns = [args.patterns.strip()]
        patterns_file = ""
    else:
        patterns, patterns_file = load_patterns(args.patterns)

    if not patterns:
        console.print("[red]No patterns found.[/red]")
        sys.exit(1)

    # Generate output prefix
    safe_pattern = patterns[0].replace("/", "_").replace("\\", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix = f"results_{safe_pattern}_{timestamp}"

    # Parse extensions
    extensions = None
    if args.extensions.strip():
        extensions = set(x.strip().lower() for x in args.extensions.split(","))

    # Run search or replace
    orchestrator = SearchOrchestrator(console, pandas=pandas, openpyxl=openpyxl)

    # === REPLACE MODE ===
    if args.replace is not None or args.replace_strings:
        # Build replacement pairs
        if args.replace_strings:
            if not os.path.isfile(args.patterns):
                console.print("[red]--replace-strings requires a file path as patterns argument.[/red]")
                sys.exit(1)
            try:
                pairs = load_replacement_pairs(args.patterns)
            except ValueError as e:
                console.print(f"[red]Error parsing replacement file: {e}[/red]")
                sys.exit(1)
            if not pairs:
                console.print("[red]No replacement pairs found in file.[/red]")
                sys.exit(1)
        elif args.replace is not None:
            if not args.single:
                console.print("[red]--replace requires --single to specify the pattern to find.[/red]")
                sys.exit(1)
            pairs = [(patterns[0], args.replace)]
        else:
            console.print("[red]No replacement pairs specified.[/red]")
            sys.exit(1)

        # Default to dry-run if neither --dry-run nor explicit write
        dry_run = args.dry_run

        replace_results = orchestrator.run_replace(
            pairs=pairs,
            directory=args.directory,
            extensions=extensions,
            threads=args.threads,
            use_rg=not args.no_rg,
            dry_run=dry_run,
            backup=args.backup,
            quiet=args.quiet,
        )

        # Generate replace reports
        if args.all_reports:
            args.html = args.excel = args.csv = args.json = True

        if args.html or args.excel or args.csv or args.json:
            orchestrator.generate_replace_reports(
                changes=replace_results["changes"],
                skipped=replace_results["skipped"],
                files_scanned=replace_results["files_scanned"],
                dry_run=dry_run,
                prefix=prefix,
                html=args.html,
                excel=args.excel,
                json=args.json,
                csv=args.csv,
                quiet=args.quiet,
            )

        return

    # === SEARCH MODE ===
    search_results = orchestrator.run(
        patterns=patterns,
        directory=args.directory,
        patterns_file=patterns_file,
        extensions=extensions,
        threads=args.threads,
        use_rg=not args.no_rg,
        quiet=args.quiet
    )

    # Generate reports
    if args.all_reports:
        args.html = args.excel = args.csv = args.json = True

    orchestrator.generate_reports(
        results=search_results["results"],
        pattern_line_hits=search_results["pattern_line_hits"],
        prefix=prefix,
        html=args.html,
        excel=args.excel,
        json=args.json,
        csv=args.csv,
        quiet=args.quiet
    )


if __name__ == "__main__":
    main()
