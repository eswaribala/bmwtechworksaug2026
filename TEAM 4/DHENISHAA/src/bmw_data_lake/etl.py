"""Local ETL pipeline for BMW telemetry and supporting datasets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .config import DEFAULT_GENERATED_DIR
from .transformations import (
    add_partition_columns,
    clean_missing_values,
    convert_timestamp_columns,
    drop_duplicate_records,
    standardize_columns,
)
from .validation import validate_dataframe


def run_local_telemetry_etl(
    input_csv: str | Path,
    output_dir: str | Path = DEFAULT_GENERATED_DIR / "curated",
    rejected_dir: str | Path | None = None,
) -> tuple[list[Path], dict[str, Any]]:
    """Read raw telemetry CSV, validate it, and write partitioned Parquet files."""

    input_path = Path(input_csv)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    if rejected_dir is None:
        rejected_root = output_root.parent / "rejected"
    else:
        rejected_root = Path(rejected_dir)
    rejected_root.mkdir(parents=True, exist_ok=True)

    telemetry_df = pd.read_csv(input_path)
    telemetry_df = standardize_columns(telemetry_df)
    telemetry_df = clean_missing_values(
        telemetry_df,
        fill_values={
            "fault_code": "UNKNOWN",
            "region": "Unknown",
            "event_date": pd.NaT,
        },
    )

    clean_df, rejected_df, summary = validate_dataframe(telemetry_df, "telemetry")
    clean_df = convert_timestamp_columns(clean_df, ["event_timestamp", "event_date"])
    clean_df = add_partition_columns(clean_df, "event_timestamp")
    clean_df = drop_duplicate_records(clean_df, subset=["vehicle_id", "event_timestamp", "battery_level"])
    clean_df = clean_df.dropna(subset=["year", "month"]).copy()

    output_files: list[Path] = []
    for (year, month), group in clean_df.groupby(["year", "month"], dropna=False):
        partition_dir = output_root / f"year={int(year)}" / f"month={int(month):02d}"
        partition_dir.mkdir(parents=True, exist_ok=True)
        file_path = partition_dir / "part-000.parquet"
        group.to_parquet(file_path, index=False)
        output_files.append(file_path)

    rejected_csv = rejected_root / "telemetry_rejected.csv"
    rejected_df.to_csv(rejected_csv, index=False)

    summary.update({
        "output_files": len(output_files),
        "rejected_csv": str(rejected_csv),
    })
    return output_files, summary


def run_local_pipeline(
    data_dir: str | Path = DEFAULT_GENERATED_DIR,
    output_dir: str | Path = DEFAULT_GENERATED_DIR / "curated",
) -> dict[str, Any]:
    """Run the local ETL flow for the generated BMW data."""

    generated_dir = Path(data_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    telemetry_input = generated_dir / "telemetry.csv"
    output_files, summary = run_local_telemetry_etl(telemetry_input, output_root)
    return {
        "telemetry_files": [str(path) for path in output_files],
        "summary": summary,
    }
