"""Ripgrep-based pattern searcher."""

from collections import defaultdict
from ..utils import run_cmd, debug, normalize_path
from .base import Searcher


class RipgrepSearcher(Searcher):
    """Search for patterns using ripgrep (rg)."""

    def search(self, patterns: list, files: list = None, patterns_file: str = None, directory: str = None, **kwargs) -> tuple:
        """
        Search for patterns using ripgrep.
        
        Args:
            patterns: List of patterns to search for
            files: Unused (ripgrep searches directory directly)
            patterns_file: Path to file containing patterns
            directory: Directory to search
            **kwargs: Unused
        
        Returns:
            (pattern_map, pattern_line_hits)
        """
        debug(f"patterns      = {patterns}")
        debug(f"patterns_file = '{patterns_file}'")
        debug(f"directory     = '{directory}'")

        # Build command
        if not patterns_file:
            debug("Mode: SINGLE PATTERN → using inline pattern")
            cmd = [
                "rg",
                "--fixed-strings",
                "--no-heading",
                "--color",
                "never",
                "-n",
                patterns[0],
                directory,
            ]
        else:
            debug("Mode: MULTI-PATTERN → using --file")
            cmd = [
                "rg",
                "--fixed-strings",
                "--no-heading",
                "--color",
                "never",
                "-n",
                "--file",
                patterns_file,
                directory,
            ]

        debug("Command to execute:")
        debug(" ".join(cmd))

        out = run_cmd(cmd)

        debug("Raw rg output:")
        debug(out)

        pattern_map = defaultdict(set)
        pattern_line_hits = defaultdict(list)

        if not out:
            return pattern_map, pattern_line_hits

        for line in out.splitlines():
            parts = line.split(":", 2)
            if len(parts) < 3:
                continue
            filepath, lineno, content = parts
            filepath = normalize_path(filepath)

            # Match against patterns
            for p in patterns:
                if p in line:
                    pattern_map[p].add(filepath)
                    pattern_line_hits[p].append({
                        "pattern": p,
                        "file": filepath,
                        "line": int(lineno),
                        "content": content
                    })

        return pattern_map, pattern_line_hits
