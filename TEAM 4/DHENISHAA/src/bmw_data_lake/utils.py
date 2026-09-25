"""Small utility functions for common project tasks."""

from __future__ import annotations

from pathlib import Path


def ensure_directory(path: str | Path) -> Path:
    """Create a directory if it doesn't already exist."""

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
