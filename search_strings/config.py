"""
Configuration and constants for search-strings tool.
"""

# Required Python modules
REQUIRED_MODULES = ["tqdm", "colorama", "pandas", "openpyxl", "rich"]

# HTML Report Template
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Search Report</title>
<style>
body { font-family: Arial; background:#121212; color:#eee; margin:20px; }
h1 { text-align:center; color:#fff; }
.subtitle { text-align:center; color:#aaa; margin-bottom:20px; }
details { background:#1e1e1e; border-radius:8px; margin-bottom:12px;
          padding:10px; border:1px solid #333; }
summary { cursor:pointer; font-size:17px; display:flex; gap:12px; }
.pattern-name { font-weight:bold; color:#fff; }
.status-badge { padding:3px 9px; border-radius:6px; font-weight:bold;
                text-transform:uppercase; font-size:12px; }
.status-badge.found { background:#2e7d32; color:#e0ffe0; }
.status-badge.missing { background:#b71c1c; color:#ffe0e0; }
.count-badge { padding:2px 7px; background:#333; color:#ccc; border-radius:5px; }
.path-list { padding:10px; border-top:1px solid #333; margin-top:8px; }
.path-item { color:#b0e0ff; font-family:monospace; padding:3px 0; }
.path-item.none { color:#777; }
</style>
</head>
<body>

<h1>Search Results Report</h1>
<div class="subtitle">Generated on {{DATE}}</div>

{{CONTENT}}

</body>
</html>
"""

# Excel styling constants
EXCEL_HEADER_COLOR = "4F81BD"
EXCEL_FOUND_COLOR = "C6EFCE"
EXCEL_MISSING_COLOR = "FFC7CE"
EXCEL_MONOSPACE_FONT = "Consolas"
EXCEL_MONOSPACE_SIZE = 9

# Replace HTML Report Template
REPLACE_HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Replace Report</title>
<style>
body { font-family: Arial; background:#121212; color:#eee; margin:20px; }
h1 { text-align:center; color:#fff; }
.subtitle { text-align:center; color:#aaa; margin-bottom:10px; }
.summary { text-align:center; color:#ccc; margin-bottom:20px; font-size:14px; }
.pairs { background:#1a1a2e; border-radius:8px; padding:12px; margin-bottom:20px; }
.pair-item { padding:4px 0; font-family:monospace; }
.old-str { color:#ff6b6b; }
.new-str { color:#51cf66; }
.count-badge { padding:2px 7px; background:#333; color:#ccc; border-radius:5px; font-size:12px; }
details { background:#1e1e1e; border-radius:8px; margin-bottom:12px;
          padding:10px; border:1px solid #333; }
summary { cursor:pointer; font-size:15px; display:flex; gap:12px; }
.file-name { font-family:monospace; color:#b0e0ff; word-break:break-all; }
.change-list { padding:10px; border-top:1px solid #333; margin-top:8px; }
.change-item { margin-bottom:10px; }
.line-num { color:#888; font-size:12px; margin-bottom:2px; }
.diff-line { font-family:monospace; padding:2px 6px; border-radius:3px; white-space:pre-wrap; word-break:break-all; }
.diff-line.removed { background:#2d1117; color:#ff6b6b; }
.diff-line.added { background:#0d2117; color:#51cf66; }
</style>
</head>
<body>

<h1>Replace Report - {{MODE}}</h1>
<div class="subtitle">Generated on {{DATE}}</div>
<div class="summary">{{SUMMARY}}</div>

<div class="pairs">
<strong>Replacement Pairs:</strong>
{{PAIRS}}
</div>

{{CONTENT}}

</body>
</html>
"""
