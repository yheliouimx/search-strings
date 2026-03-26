"""File-based string replacer with dry-run support."""

import os
import sys
import shutil
import tempfile
from ..utils import debug, normalize_path
from .base import Replacer


def _long_path(filepath):
    """Ensure Windows long paths (>260 chars) work by adding extended-length prefix."""
    if sys.platform == "win32" and os.path.isabs(filepath) and not filepath.startswith("\\\\?\\"):
        # Extended-length prefix requires backslashes
        return "\\\\?\\" + filepath.replace("/", "\\")
    return filepath


def _is_binary(filepath, sample_size=8192):
    """Detect binary files by checking for null bytes (excluding BOM/UTF-16)."""
    try:
        with open(_long_path(filepath), "rb") as f:
            chunk = f.read(sample_size)
        # UTF-16 BOM or UTF-8 BOM → text file
        if chunk[:2] in (b"\xff\xfe", b"\xfe\xff") or chunk[:3] == b"\xef\xbb\xbf":
            return False
        # Check for null bytes outside of UTF-16 patterns
        # If every other byte is null, it's likely UTF-16
        if b"\x00" in chunk:
            # Simple UTF-16 LE heuristic: \x00 only at odd positions
            non_null = chunk.replace(b"\x00", b"")
            if len(non_null) > len(chunk) * 0.3:
                return False  # Likely UTF-16 text
            return True
        return False
    except (OSError, IOError):
        return True


def _detect_encoding(filepath):
    """Detect file encoding by checking BOM and byte patterns."""
    try:
        with open(_long_path(filepath), "rb") as f:
            raw = f.read(8192)
    except (OSError, IOError):
        return "utf-8"

    if not raw:
        return "utf-8"

    # Check BOM
    if raw[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"
    if raw[:2] == b"\xff\xfe":
        return "utf-16-le"
    if raw[:2] == b"\xfe\xff":
        return "utf-16-be"

    # Detect UTF-16 without BOM by checking for null byte patterns
    # UTF-16-LE: every odd byte tends to be \x00 for ASCII-range text
    # UTF-16-BE: every even byte tends to be \x00 for ASCII-range text
    sample = raw[:256] if len(raw) >= 256 else raw
    if len(sample) >= 2:
        odd_nulls = sum(1 for i in range(1, len(sample), 2) if sample[i:i+1] == b"\x00")
        even_nulls = sum(1 for i in range(0, len(sample), 2) if sample[i:i+1] == b"\x00")
        half = len(sample) // 2
        if half > 0:
            if odd_nulls / half > 0.5:
                return "utf-16-le"
            if even_nulls / half > 0.5:
                return "utf-16-be"

    # Try UTF-8, fall back to latin-1 (never fails)
    try:
        with open(_long_path(filepath), "r", encoding="utf-8") as f:
            f.read(8192)
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"


class FileReplacer(Replacer):
    """Replace strings in files with dry-run and backup support."""

    def replace(self, pairs: list, files: list, dry_run: bool = True,
                backup: bool = False, rg_validated: bool = False) -> list:
        """
        Replace old strings with new strings in the given files.

        Args:
            pairs: List of (old_string, new_string) tuples
            files: List of file paths to process
            dry_run: If True, report changes without writing
            backup: If True, create .bak copies before modifying
            rg_validated: If True, skip binary detection (ripgrep already filtered)

        Returns:
            Tuple of (changes list, skipped list)
        """
        changes = []
        skipped = []

        for filepath in files:
            if not rg_validated and _is_binary(filepath):
                debug(f"Skipping binary file: {filepath}")
                skipped.append({"file": normalize_path(filepath), "reason": "binary"})
                continue

            file_changes = self._process_file(filepath, pairs, dry_run, backup)
            changes.extend(file_changes)

        return changes, skipped

    def _process_file(self, filepath: str, pairs: list, dry_run: bool,
                      backup: bool) -> list:
        """Process a single file for all replacement pairs."""
        changes = []
        norm_path = normalize_path(filepath)
        encoding = _detect_encoding(filepath)
        debug(f"File {filepath} detected encoding: {encoding}")

        try:
            with open(_long_path(filepath), "r", encoding=encoding) as f:
                original_lines = f.readlines()
        except UnicodeDecodeError:
            debug(f"Skipping file with encoding error: {filepath}")
            return changes
        except FileNotFoundError:
            debug(f"File not found (path may contain special characters): {filepath}")
            return changes
        except (OSError, IOError) as e:
            debug(f"Cannot read {filepath}: {e}")
            return changes

        modified_lines = list(original_lines)
        file_has_changes = False

        for line_idx, line in enumerate(original_lines):
            for old, new in pairs:
                if old in line:
                    new_line = line.replace(old, new)
                    changes.append({
                        "file": norm_path,
                        "line": line_idx + 1,
                        "old": old,
                        "new": new,
                        "content_before": line.rstrip("\n\r"),
                        "content_after": new_line.rstrip("\n\r"),
                        "applied": not dry_run,
                    })
                    modified_lines[line_idx] = new_line
                    file_has_changes = True

        if file_has_changes and not dry_run:
            self._write_file(filepath, original_lines, modified_lines, backup,
                             encoding)

        return changes

    def _write_file(self, filepath: str, original_lines: list,
                    modified_lines: list, backup: bool, encoding: str = "utf-8"):
        """Atomically write modified content to file."""
        safe_path = _long_path(filepath)
        if backup:
            shutil.copy2(safe_path, safe_path + ".bak")
            debug(f"Backup created: {filepath}.bak")

        # Atomic write: write to temp file then replace
        dir_name = os.path.dirname(safe_path) or "."
        try:
            fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
            with os.fdopen(fd, "w", encoding=encoding) as tmp:
                tmp.writelines(modified_lines)
            os.replace(tmp_path, safe_path)
            debug(f"Written: {filepath}")
        except (OSError, IOError) as e:
            debug(f"Failed to write {filepath}: {e}")
            # Clean up temp file on failure
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
