"""
BMW Data Quality & Governance Platform — Validator
Participant 12 | Pod D
All individual validation rule implementations, powered by PySpark.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window
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


def check_schema(df: DataFrame, dataset: str) -> list[str]:
    """
    Verify all required columns are present.
    Returns list of missing column names.
    """
    required = REQUIRED_COLUMNS.get(dataset, [])
    missing = [col for col in required if col not in df.columns]
    return missing


def check_nulls(df: DataFrame, dataset: str) -> DataFrame:
    """
    Flag rows that have NULL values in any required column.

    Returns df with a boolean column '__null_fail' and a string
    column '__null_cols' listing which columns are null.
    """
    required = REQUIRED_COLUMNS.get(dataset, [])
    cols_present = [c for c in required if c in df.columns]

    if not cols_present:
        return df.withColumn("__null_fail", F.lit(False)).withColumn("__null_cols", F.lit(""))

    null_flags = [F.when(F.col(c).isNull(), F.lit(c)) for c in cols_present]
    df = df.withColumn("__null_cols", F.concat_ws(", ", *null_flags))
    df = df.withColumn("__null_fail", F.length(F.col("__null_cols")) > 0)
    return df


def check_duplicates(df: DataFrame, dataset: str) -> DataFrame:
    """
    Flag duplicate rows based on the dataset's unique key columns.
    The first occurrence (by original row order) is kept; later
    occurrences are flagged. Returns df with boolean column '__dup_fail'.
    """
    key_cols = [c for c in UNIQUE_KEY_COLUMNS.get(dataset, []) if c in df.columns]

    df = df.withColumn("__row_id", F.monotonically_increasing_id())

    if key_cols:
        window = Window.partitionBy(*key_cols).orderBy("__row_id")
        df = df.withColumn("__dup_rank", F.row_number().over(window))
        df = df.withColumn("__dup_fail", F.col("__dup_rank") > 1).drop("__dup_rank")
    else:
        df = df.withColumn("__dup_fail", F.lit(False))

    # Preserve original ingestion order downstream
    return df.orderBy("__row_id")


def check_vin(df: DataFrame) -> DataFrame:
    """
    Validate VIN values against the BMW VIN format.
    Standard VIN: 17 alphanumeric chars (no I, O, Q).

    Returns df with boolean column '__vin_fail'.
    """
    if VIN_COLUMN not in df.columns:
        return df.withColumn("__vin_fail", F.lit(False))

    normalized = F.upper(F.trim(F.col(VIN_COLUMN)))
    valid = F.col(VIN_COLUMN).isNotNull() & normalized.rlike(VIN_REGEX)
    return df.withColumn("__vin_fail", ~valid)


def check_dates(df: DataFrame, dataset: str) -> DataFrame:
    """
    Validate date / timestamp fields.
    Accepts ISO 8601 (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS).

    Returns df with boolean column '__date_fail' and '__date_cols'.
    """
    date_cols = [c for c in DATE_COLUMNS.get(dataset, []) if c in df.columns]

    if not date_cols:
        return df.withColumn("__date_fail", F.lit(False)).withColumn("__date_cols", F.lit(""))

    fail_flags = []
    for col in date_cols:
        # try_to_timestamp returns NULL on unparseable input instead of raising
        # (Spark's ANSI mode makes plain to_timestamp throw on bad strings).
        parsed = F.coalesce(
            F.try_to_timestamp(F.col(col), F.lit("yyyy-MM-dd HH:mm:ss")),
            F.try_to_timestamp(F.col(col), F.lit("yyyy-MM-dd")),
        )
        fail_flags.append(F.when(parsed.isNull(), F.lit(col)))

    df = df.withColumn("__date_cols", F.concat_ws(", ", *fail_flags))
    df = df.withColumn("__date_fail", F.length(F.col("__date_cols")) > 0)
    return df


def check_ranges(df: DataFrame) -> DataFrame:
    """
    Check numeric columns against configured min/max ranges.

    Returns df with boolean column '__range_fail' and '__range_cols'.
    """
    applicable = {col: bounds for col, bounds in RANGE_RULES.items() if col in df.columns}

    if not applicable:
        return df.withColumn("__range_fail", F.lit(False)).withColumn("__range_cols", F.lit(""))

    fail_flags = []
    for col, (lo, hi) in applicable.items():
        numeric = F.col(col).cast("double")
        out_of_bounds = numeric.isNull() | (numeric < F.lit(lo)) | (numeric > F.lit(hi))
        fail_flags.append(F.when(out_of_bounds, F.lit(col)))

    df = df.withColumn("__range_cols", F.concat_ws(", ", *fail_flags))
    df = df.withColumn("__range_fail", F.length(F.col("__range_cols")) > 0)
    return df


def check_referential_integrity(
    df: DataFrame,
    fk_column: str,
    reference_df: DataFrame,
    pk_column: str,
) -> DataFrame:
    """
    Verify that every value in fk_column exists in the reference DataFrame's pk_column.

    Returns df with boolean column '__ref_fail'.
    """
    if fk_column not in df.columns:
        return df.withColumn("__ref_fail", F.lit(False))

    df = df.withColumn("__row_id", F.monotonically_increasing_id())

    ref = (
        reference_df
        .select(F.col(pk_column).alias("__ref_pk"))
        .where(F.col("__ref_pk").isNotNull())
        .distinct()
        .withColumn("__ref_exists", F.lit(True))
    )

    joined = df.join(ref, df[fk_column] == ref["__ref_pk"], "left")
    joined = joined.withColumn("__ref_fail", F.col("__ref_exists").isNull())
    joined = joined.drop("__ref_pk", "__ref_exists")

    return joined.orderBy("__row_id")


# ─────────────────────────────────────────────────────
# Null percentage summary helper
# ─────────────────────────────────────────────────────
def null_summary(df: DataFrame, dataset: str) -> list[dict]:
    """Return per-column null statistics for important columns."""
    required = REQUIRED_COLUMNS.get(dataset, [])
    cols = [c for c in required if c in df.columns]
    total = df.count()

    if not cols or total == 0:
        return []

    agg_exprs = [F.sum(F.col(c).isNull().cast("int")).alias(c) for c in cols]
    row = df.select(*agg_exprs).collect()[0]

    results = []
    for col in cols:
        null_count = int(row[col] or 0)
        null_pct = round(null_count / total * 100, 2) if total else 0.0
        results.append({"column": col, "null_count": null_count, "null_pct": null_pct})
    return results
