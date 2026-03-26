<p align="center">
  <img src="assets/search-strings-logo.png" alt="search-strings logo" width="400">
</p>

# search-strings

High-performance recursive pattern search tool with multi-format reporting.

`search-strings` scans files in a directory tree for one or more string patterns, combines filename and content matches, and can generate reports in HTML, Excel, CSV, and JSON.

## Features

- Recursive search across a directory tree
- Search modes:
  - Pattern list from file (one pattern per line)
  - Single literal pattern from CLI
- **Replace mode**: find and replace strings across files
  - Single pair from CLI or bulk pairs from file
  - Dry-run preview before applying changes
  - Backup support (`.bak` files)
  - Atomic writes to prevent corruption
  - Smart encoding detection (UTF-8, UTF-16, BOM-aware)
  - Windows long path support (>260 characters)
- Smart search engine selection:
  - Uses `ripgrep` (`rg`) when available for best performance
  - Falls back to `grep` automatically
- Optional file extension filtering
- Multiple report outputs: HTML, Excel, CSV, JSON
- Rich terminal output (unless `--quiet`)

## Requirements

- Python 3.7+
- For best performance: `ripgrep` installed and available on PATH

Python package dependencies are handled by pip:

- `tqdm`
- `colorama`
- `pandas`
- `openpyxl`
- `rich`

## Installation

### Option 1: Install from source (local project)

```bash
pip install .
```

For development install:

```bash
pip install -e .[dev]
```

### Option 2: Build and install wheel

```bash
python -m pip install --upgrade build
python -m build
pip install dist/*.whl
```

## Usage

```bash
search-strings PATTERNS DIRECTORY [OPTIONS]
```

- `PATTERNS`:
  - Path to a patterns file (default behavior), or
  - Single literal pattern when `--single` is used
- `DIRECTORY`: Root directory to search recursively

### Basic examples

Search patterns from file:

```bash
search-strings patterns.txt /path/to/search --excel --html
```

Search a single literal pattern:

```bash
search-strings "search_term" /path/to/search --single --all-reports
```

Filter by extensions:

```bash
search-strings patterns.txt . --extensions xml,txt,json
```

Force grep fallback and use custom threads:

```bash
search-strings patterns.txt . --no-rg --threads 8
```

Quiet mode (no terminal output):

```bash
search-strings patterns.txt . --json --quiet
```

## CLI Options

| Option | Type | Default | Description |
|---|---|---|---|
| `--single` | flag | `false` | Treat `PATTERNS` as a literal pattern, not a file |
| `--extensions` | string | `""` | Comma-separated extensions filter (example: `xml,txt,json`) |
| `--threads` | int | `os.cpu_count()` | Number of threads used by grep fallback |
| `--html` | flag | `false` | Generate HTML report |
| `--excel` | flag | `false` | Generate Excel report (`.xlsx`) |
| `--csv` | flag | `false` | Generate CSV report |
| `--json` | flag | `false` | Generate JSON report |
| `--all-reports` | flag | `false` | Generate all report formats |
| `--no-rg` | flag | `false` | Do not use ripgrep; force grep fallback |
| `--quiet` | flag | `false` | Suppress console output |
| `--yes` | flag | `false` | Auto-install missing Python dependencies without prompt |
| `--debug` | flag | `false` | Enable detailed debug logs |
| `--replace VALUE` | string | - | Replace matched pattern with `VALUE` (use with `--single`) |
| `--replace-strings` | flag | `false` | Treat patterns file as replacement pairs (`old\|new` per line) |
| `--dry-run` | flag | `false` | Preview replacements without modifying files |
| `--backup` | flag | `false` | Create `.bak` copies before replacing |

## Input Patterns File Format

A plain text file with one pattern per line:

```text
customer_id
/opt/app/config
ERROR_42
```

Empty lines are ignored.

## Replace Mode

### Single pair replacement

Preview changes (dry-run):

```bash
search-strings "old_text" /path/to/search --single --replace "new_text" --dry-run
```

Apply changes:

```bash
search-strings "old_text" /path/to/search --single --replace "new_text"
```

Apply with backup:

```bash
search-strings "old_text" /path/to/search --single --replace "new_text" --backup
```

### Bulk replacement from file

Create a replacements file with `old|new` pairs, one per line:

```text
customer_id|client_id
old_config|new_config
ERROR_42|WARNING_42
```

Use `\|` to include a literal pipe character in the strings.

Preview:

```bash
search-strings replacements.txt /path/to/search --replace-strings --dry-run
```

Apply:

```bash
search-strings replacements.txt /path/to/search --replace-strings
```

### Replace with reports

Generate HTML/Excel/CSV/JSON reports of all changes:

```bash
search-strings "old_text" /path --single --replace "new_text" --dry-run --all-reports
```

### Dry-run output

The dry-run shows a diff-style preview for each change:

```
file/path/config.xml
  Line 12
  --- <value>customer_id</value>
  +++ <value>client_id</value>
```

Followed by a summary:

```
==================================================
  Dry Run Summary
==================================================
  Files scanned:      142
  Files would be modified:  5
  Total replacements: 12

  Pairs:
    customer_id -> client_id  (12 matches)
==================================================
```

## Output

When report flags are enabled, output files are created in the current working directory with this naming style:

- `results_<first_pattern>_<timestamp>.html`
- `results_<first_pattern>_<timestamp>.xlsx`
- `results_<first_pattern>_<timestamp>.csv`
- `results_<first_pattern>_<timestamp>.json`

## Entry Points

You can run the tool using any of these:

```bash
search-strings ...
python -m search_strings ...
python run.py ...
python search-strings.py ...
```

## Packaging for Distribution

Build artifacts:

```bash
python -m build
```

This generates:

- Source distribution: `dist/*.tar.gz`
- Wheel: `dist/*.whl`

Upload with Twine (example):

```bash
python -m pip install --upgrade twine
python -m twine check dist/*
python -m twine upload dist/*
```

Use an internal package index if this tool is for your organization only.

## License

MIT
