"""Rich terminal UI output."""

from rich import box


def rich_summary(results_list, Console, Table, Text):
    """Display search summary in a formatted table."""
    table = Table(title="Search Summary", show_lines=True, box=box.SIMPLE_HEAVY)

    table.add_column("Pattern", style="cyan", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    table.add_column("Count", justify="right")

    for item in results_list:
        p = item["pattern"]
        status = item["status"]
        emoji = "✔" if status == "FOUND" else "✘"

        if status == "FOUND":
            status_text = Text(f"{emoji} FOUND", style="bold green")
        else:
            status_text = Text(f"{emoji} MISSING", style="bold red")

        table.add_row(p, status_text, str(len(item["paths"])))

    Console().print(table)


def rich_details(results_list, Console, Panel, Text):
    """Display detailed results in expandable panels."""
    console = Console()

    for item in results_list:
        p = item["pattern"]
        status = item["status"]
        count = len(item["paths"])

        # Color-coded title
        if status == "FOUND":
            title = Text(f"{p}  —  FOUND ({count})", style="bold green")
            border = "green"
        else:
            title = Text(f"{p}  —  MISSING", style="bold red")
            border = "red"

        # Body
        if item["paths"]:
            content = "\n".join(item["paths"])
        else:
            content = "No matches found"

        # Auto-fitting panel
        panel = Panel.fit(content, title=title, border_style=border, padding=(1, 2))

        console.print(panel)
        console.print()  # spacing between panels
