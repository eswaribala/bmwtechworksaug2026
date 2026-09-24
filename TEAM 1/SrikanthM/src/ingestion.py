from __future__ import annotations

from pathlib import Path

from pyspark.sql import DataFrame, SparkSession


def read_csv_files(spark: SparkSession, base_path: str | Path) -> dict[str, DataFrame]:
    """Read the raw source CSV files into Spark DataFrames."""
    base = Path(base_path)
    files = {
        "telemetry": base / "telemetry.csv",
        "vehicle_master": base / "vehicle_master.csv",
        "charging_sessions": base / "charging_sessions.csv",
    }

    return {
        name: spark.read.option("header", True).option("inferSchema", True).csv(str(path))
        for name, path in files.items()
    }
