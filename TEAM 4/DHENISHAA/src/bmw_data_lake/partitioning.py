"""Partition helper functions for BMW telemetry data."""

from __future__ import annotations

from pathlib import Path


def telemetry_partition_path(year: int, month: int, region: str | None = None) -> str:
    """Return an S3 or local partition path in a common telemetry layout."""

    if region is None:
        return f"year={year}/month={month:02d}"
    return f"region={region}/year={year}/month={month:02d}"


def build_partition_directory(base_dir: str | Path, year: int, month: int, region: str | None = None) -> Path:
    """Create a partition directory path for local file output."""

    base = Path(base_dir)
    partition_path = Path(telemetry_partition_path(year, month, region=region))
    return base / partition_path
