"""
BMW Data Quality & Governance Platform — Validator
Participant 12 | Pod D
All individual validation rule implementations.
"""

import re
import pandas as pd
from datetime import datetime
from typing import Optional
from src.utils.config import (
    REQUIRED_COLUMNS, VIN_REGEX, VIN_COLUMN,
    RANGE_RULES, DATE_COLUMNS, UNIQUE_KEY_COLUMNS
)


# ─────────────────────────────────────────────────────
# Error type constants
# ─────────────────────────────────────────────────────
ERROR_NULL = "NULL_VALUE"
ERROR_DUPLICATE = "DUPLICATE_RECORD"
ERROR_VIN = "INVALID_VIN"
ERROR_DATE = "INVALID_DATE"
ERROR_RANGE = "OUT_OF_RANGE"
ERROR_REFERENTIAL = "REFERENTIAL_INTEGRITY"
ERROR_SCHEMA = "SCHEMA_ERROR"


def check_schema(df: pd.DataFrame, dataset: str) -> list[str]:
    """
    Verify all required columns are present.
    Returns list of missing column names.
    """
    required = REQUIRED_COLUMNS.get(dataset, [])
    missing = [col for col in required if col not in df.columns]
    return missing


def check_nulls(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """
    Flag rows that have NULL values in any required column.

    Returns a copy of df with a boolean column '__null_fail' and
    a string column '__null_cols' listing which columns are null.
    """
    df = df.copy()
    required = REQUIRED_COLUMNS.get(dataset, [])
    cols_present = [c for c in required if c in df.columns]

    null_mask = df[cols_present].isnull().any(axis=1)
    df["__null_fail"] = null_mask

    def _null_cols(row):
        return ", ".join(c for c in cols_present if pd.isnull(row[c]))

    df["__null_cols"] = df.apply(_null_cols, axis=1)
    return df


def check_duplicates(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """
    Flag duplicate rows based on the dataset's unique key columns.

    Returns df with boolean column '__dup_fail'.
    """
    df = df.copy()
    key_cols = UNIQUE_KEY_COLUMNS.get(dataset, [])
    key_cols_present = [c for c in key_cols if c in df.columns]

    if key_cols_present:
        df["__dup_fail"] = df.duplicated(subset=key_cols_present, keep="first")
    else:
        df["__dup_fail"] = False
    return df


def check_vin(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate VIN values against the BMW VIN format.
    Standard VIN: 17 alphanumeric chars (no I, O, Q).

    Returns df with boolean column '__vin_fail'.
    """
    df = df.copy()
    if VIN_COLUMN not in df.columns:
        df["__vin_fail"] = False
        return df

    vin_pattern = re.compile(VIN_REGEX)

    def _valid_vin(v) -> bool:
        if pd.isnull(v):
            return False
        return bool(vin_pattern.match(str(v).strip().upper()))

    df["__vin_fail"] = ~df[VIN_COLUMN].apply(_valid_vin)
    return df


def check_dates(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """
    Validate date / timestamp fields.
    Accepts ISO 8601 (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS).

    Returns df with boolean column '__date_fail' and '__date_cols'.
    """
    df = df.copy()
    date_cols = [c for c in DATE_COLUMNS.get(dataset, []) if c in df.columns]

    if not date_cols:
        df["__date_fail"] = False
        df["__date_cols"] = ""
        return df

    date_fail_masks = []
    for col in date_cols:
        parsed = pd.to_datetime(df[col], errors="coerce")
        date_fail_masks.append(parsed.isnull())

    combined = pd.concat(date_fail_masks, axis=1)
    combined.columns = date_cols
    df["__date_fail"] = combined.any(axis=1)
    df["__date_cols"] = combined.apply(
        lambda row: ", ".join(col for col in date_cols if row[col]), axis=1
    )
    return df


def check_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check numeric columns against configured min/max ranges.

    Returns df with boolean column '__range_fail' and '__range_cols'.
    """
    df = df.copy()
    applicable = {col: bounds for col, bounds in RANGE_RULES.items() if col in df.columns}

    if not applicable:
        df["__range_fail"] = False
        df["__range_cols"] = ""
        return df

    fail_masks = {}
    for col, (lo, hi) in applicable.items():
        numeric = pd.to_numeric(df[col], errors="coerce")
        fail_masks[col] = (numeric < lo) | (numeric > hi) | numeric.isnull()

    fail_df = pd.DataFrame(fail_masks)
    df["__range_fail"] = fail_df.any(axis=1)
    df["__range_cols"] = fail_df.apply(
        lambda row: ", ".join(col for col in fail_masks if row[col]), axis=1
    )
    return df


def check_referential_integrity(
    df: pd.DataFrame,
    fk_column: str,
    reference_df: pd.DataFrame,
    pk_column: str,
) -> pd.DataFrame:
    """
    Verify that every value in fk_column exists in the reference DataFrame's pk_column.

    Returns df with boolean column '__ref_fail'.
    """
    df = df.copy()
    if fk_column not in df.columns:
        df["__ref_fail"] = False
        return df

    valid_ids = set(reference_df[pk_column].dropna().unique())
    df["__ref_fail"] = ~df[fk_column].isin(valid_ids)
    return df


# ─────────────────────────────────────────────────────
# Null percentage summary helper
# ─────────────────────────────────────────────────────
def null_summary(df: pd.DataFrame, dataset: str) -> list[dict]:
    """Return per-column null statistics for important columns."""
    required = REQUIRED_COLUMNS.get(dataset, [])
    cols = [c for c in required if c in df.columns]
    total = len(df)
    results = []
    for col in cols:
        null_count = int(df[col].isnull().sum())
        null_pct = round(null_count / total * 100, 2) if total else 0.0
        results.append({"column": col, "null_count": null_count, "null_pct": null_pct})
    return results
