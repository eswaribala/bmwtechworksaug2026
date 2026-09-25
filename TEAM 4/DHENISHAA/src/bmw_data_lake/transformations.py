"""Transformation utilities for BMW datasets."""

from __future__ import annotations

from typing import Any

import pandas as pd


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize and lower-case column names."""

    renamed = {column: str(column).strip().lower().replace(" ", "_") for column in df.columns}
    return df.rename(columns=renamed)


def convert_timestamp_columns(df: pd.DataFrame, timestamp_columns: list[str] | None = None) -> pd.DataFrame:
    """Convert selected timestamp columns to pandas datetime."""

    result = df.copy()
    columns = timestamp_columns or ["event_timestamp", "service_date", "sale_date", "claim_date", "manufacture_date"]
    for column in columns:
        if column in result.columns:
            result[column] = pd.to_datetime(result[column], errors="coerce")
    return result


def add_partition_columns(df: pd.DataFrame, date_column: str = "event_timestamp") -> pd.DataFrame:
    """Add year and month partitioning columns for telemetry analysis."""

    result = df.copy()
    if date_column in result.columns:
        result["year"] = pd.to_datetime(result[date_column], errors="coerce").dt.year
        result["month"] = pd.to_datetime(result[date_column], errors="coerce").dt.month
    return result


def drop_duplicate_records(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """Remove duplicate records based on selected columns."""

    if subset is None:
        subset = list(df.columns)
    return df.drop_duplicates(subset=subset)


def clean_missing_values(df: pd.DataFrame, fill_values: dict[str, Any] | None = None) -> pd.DataFrame:
    """Fill missing values conservatively for analysis."""

    result = df.copy()
    if fill_values:
        for column, value in fill_values.items():
            if column in result.columns:
                result[column] = result[column].fillna(value)
    return result


def calculate_summary(df: pd.DataFrame) -> dict[str, float | int]:
    """Compute a simple summary for local QA."""

    summary = {
        "row_count": int(len(df)),
        "average_battery_level": float(df["battery_level"].mean()) if "battery_level" in df.columns else 0.0,
        "average_temperature": float(df["battery_temperature"].mean()) if "battery_temperature" in df.columns else 0.0,
    }
    return summary
