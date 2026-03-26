"""HTML report generator."""

from datetime import datetime
from ..config import HTML_TEMPLATE
from .base import Reporter


class HtmlReporter(Reporter):
    """Generate HTML reports."""

    def generate(self, results: list, pattern_line_hits: dict, output_file: str, **kwargs):
        """Generate an HTML report."""
        html = HTML_TEMPLATE.replace(
            "{{DATE}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        blocks = []
        for item in results:
            p = item["pattern"]
            status = item["status"]
            paths = item["paths"]
            cls = "found" if status == "FOUND" else "missing"

            part = f"""
        <details>
            <summary>
                <span class="pattern-name">{p}</span>
                <span class="status-badge {cls}">{status}</span>
                <span class="count-badge">{len(paths)}</span>
            </summary>
            <div class="path-list">
        """
            if paths:
                for fp in paths:
                    part += f"<div class='path-item'>{fp}</div>"
            else:
                part += "<div class='path-item none'>No files found</div>"

            part += "</div></details>"
            blocks.append(part)

        html = html.replace("{{CONTENT}}", "\n".join(blocks))

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
