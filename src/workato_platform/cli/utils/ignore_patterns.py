"""Utility functions for handling .workato-ignore patterns"""

import fnmatch

from pathlib import Path


def load_ignore_patterns(workspace_root: Path) -> set[str]:
    """Load patterns from .workato-ignore file"""
    ignore_file = workspace_root / ".workato-ignore"
    patterns = {".workatoenv"}  # Always protect config file

    if not ignore_file.exists():
        return patterns

    try:
        with open(ignore_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.add(line)
    except (OSError, UnicodeDecodeError):
        # If we can't read the ignore file, just use defaults
        pass

    return patterns


def should_skip_file(file_path: Path, ignore_patterns: set[str]) -> bool:
    """Check if file should be skipped using .workato-ignore patterns"""
    path_str = str(file_path)
    file_name = file_path.name

    for pattern in ignore_patterns:
        # Check exact matches, glob patterns, and filename patterns
        if (fnmatch.fnmatch(path_str, pattern) or
            fnmatch.fnmatch(file_name, pattern) or
            path_str.startswith(pattern + "/") or
            path_str.startswith(pattern + "\\")):
            return True

    return False
