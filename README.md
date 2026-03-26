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

## Input Patterns File Format

A plain text file with one pattern per line:

```text
customer_id
/opt/app/config
ERROR_42
```

Empty lines are ignored.

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
