"""Data-quality validation utilities for BMW data sources."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd

from .exceptions import DataValidationError


def is_valid_vin(value: Any) -> bool:
    """Very simple VIN validation for synthetic data."""

    if pd.isna(value):
        return False
    text = str(value).strip().upper()
    return len(text) >= 10 and text.isalnum()


def valid_region(value: Any) -> bool:
    """Check whether region is in the approved set."""

    return str(value).strip() in {"North America", "Europe", "Asia Pacific", "Middle East"}


def validate_dataframe(df: pd.DataFrame, dataset_name: str) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Validate a DataFrame and return clean, rejected, and summary data."""

    if df.empty:
        raise DataValidationError(f"Dataset {dataset_name} is empty.")

    clean_rows: list[dict[str, Any]] = []
    rejected_rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "total_rows": len(df),
        "clean_rows": 0,
        "rejected_rows": 0,
        "reasons": {},
    }

    for _, row in df.iterrows():
        issues: list[str] = []

        if "vehicle_id" in df.columns:
            vehicle_id = row.get("vehicle_id")
            if pd.isna(vehicle_id) or str(vehicle_id).strip() == "":
                issues.append("missing_vehicle_id")

        if "vin" in df.columns and not is_valid_vin(row.get("vin")):
            issues.append("invalid_vin")

        if "event_timestamp" in df.columns:
            ts = row.get("event_timestamp")
            if pd.isna(ts) or str(ts).strip() == "":
                issues.append("missing_event_timestamp")
            else:
                try:
                    pd.to_datetime(ts)
                except (ValueError, TypeError):
                    issues.append("invalid_timestamp")

        if "region" in df.columns and not valid_region(row.get("region")):
            issues.append("invalid_region")

        if "battery_level" in df.columns:
            value = row.get("battery_level")
            try:
                numeric_value = float(value)
                if not 0 <= numeric_value <= 100:
                    issues.append("invalid_battery_level")
            except (TypeError, ValueError):
                issues.append("invalid_battery_level")

        if "battery_temperature" in df.columns:
            value = row.get("battery_temperature")
            try:
                numeric_value = float(value)
                if not -60 <= numeric_value <= 120:
                    issues.append("invalid_temperature")
            except (TypeError, ValueError):
                issues.append("invalid_temperature")

        if "speed_kmh" in df.columns:
            value = row.get("speed_kmh")
            try:
                numeric_value = float(value)
                if math.isnan(numeric_value) or numeric_value < 0:
                    issues.append("invalid_speed")
            except (TypeError, ValueError):
                issues.append("invalid_speed")

        if issues:
            rejected_rows.append(row.to_dict())
            for reason in issues:
                summary["reasons"][reason] = summary["reasons"].get(reason, 0) + 1
        else:
            clean_rows.append(row.to_dict())

    clean_df = pd.DataFrame(clean_rows, columns=df.columns)
    rejected_df = pd.DataFrame(rejected_rows, columns=df.columns)
    summary["clean_rows"] = len(clean_df)
    summary["rejected_rows"] = len(rejected_df)
    return clean_df, rejected_df, summary
