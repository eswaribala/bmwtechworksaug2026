"""
BMW Data Quality & Governance Platform — Quality Engine
Participant 12 | Pod D
Orchestrates all validators, routes records to valid/invalid partitions.
Powered by PySpark for distributed dataset processing.
"""

from datetime import datetime, timezone
from typing import Optional
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from src.utils.logger import BmwLogger
from src.utils.config import REFERENTIAL_RULES
from src.processing.validator import (
    check_schema, check_nulls, check_duplicates, check_vin,
    check_dates, check_ranges, check_referential_integrity, null_summary,
    ERROR_NULL, ERROR_DUPLICATE, ERROR_VIN, ERROR_DATE, ERROR_RANGE,
    ERROR_REFERENTIAL, ERROR_SCHEMA,
)


class QualityMetrics:
    """Holds the full set of quality check results for one dataset run."""

    def __init__(self, dataset: str, total_records: int):
        self.dataset = dataset
        self.total_records = total_records
        self.schema_errors: list[str] = []
        self.null_count: int = 0
        self.duplicate_count: int = 0
        self.invalid_vin_count: int = 0
        self.invalid_date_count: int = 0
        self.range_violation_count: int = 0
        self.referential_error_count: int = 0
        self.valid_records: int = 0
        self.rejected_records: int = 0
        self.quality_score: float = 0.0
        self.score_label: str = ""
        self.null_summary: list[dict] = []
        self.execution_time: str = datetime.now(timezone.utc).isoformat()
        self.duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        return {
            "dataset": self.dataset,
            "execution_time": self.execution_time,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "rejected_records": self.rejected_records,
            "null_count": self.null_count,
            "duplicate_count": self.duplicate_count,
            "invalid_vin_count": self.invalid_vin_count,
            "invalid_date_count": self.invalid_date_count,
            "range_violation_count": self.range_violation_count,
            "referential_error_count": self.referential_error_count,
            "quality_score": self.quality_score,
            "score_label": self.score_label,
            "null_summary": self.null_summary,
            "duration_seconds": self.duration_seconds,
        }


class QualityEngine:
    """
    Main orchestrator — runs all validation checks with PySpark and separates
    valid records (curated) from invalid records (quarantine).
    """

    def __init__(self, dataset: str, logger: Optional[BmwLogger] = None):
        self.dataset = dataset
        self.logger = logger or BmwLogger(dataset)

    def run(
        self,
        df: DataFrame,
        reference_df: Optional[DataFrame] = None,
    ) -> tuple[DataFrame, DataFrame, QualityMetrics]:
        """
        Execute the full quality pipeline on df.

        Args:
            df:           Input raw Spark DataFrame.
            reference_df: Vehicle master Spark DataFrame for referential checks.

        Returns:
            (valid_df, invalid_df, metrics)
        """
        import time
        start = time.time()

        df = df.cache()
        total = df.count()
        metrics = QualityMetrics(dataset=self.dataset, total_records=total)
        self.logger.pipeline_start()
        self.logger.info(f"Dataset: {self.dataset}")
        self.logger.records_received(total)

        # ── 1. Schema check ───────────────────────────────────
        missing_cols = check_schema(df, self.dataset)
        if missing_cols:
            metrics.schema_errors = missing_cols
            self.logger.error(f"Schema error — missing columns: {missing_cols}")

        # ── 2. Null check ─────────────────────────────────────
        df = check_nulls(df, self.dataset)
        metrics.null_summary = null_summary(df, self.dataset)

        # ── 3. Duplicate check ────────────────────────────────
        df = check_duplicates(df, self.dataset)

        # ── 4. VIN check ──────────────────────────────────────
        df = check_vin(df)

        # ── 5. Date check ─────────────────────────────────────
        df = check_dates(df, self.dataset)

        # ── 6. Range check ────────────────────────────────────
        df = check_ranges(df)

        # ── 7. Referential integrity ──────────────────────────
        if reference_df is not None and self.dataset in REFERENTIAL_RULES:
            fk_col, _parent, pk_col = REFERENTIAL_RULES[self.dataset]
            df = check_referential_integrity(df, fk_col, reference_df, pk_col)
        else:
            df = df.withColumn("__ref_fail", F.lit(False))

        # ── 8. Combine failure flags ──────────────────────────
        fail_cols = [
            "__null_fail", "__dup_fail", "__vin_fail",
            "__date_fail", "__range_fail", "__ref_fail",
        ]
        df = df.withColumn(
            "__any_fail",
            F.col(fail_cols[0]) | F.col(fail_cols[1]) | F.col(fail_cols[2]) |
            F.col(fail_cols[3]) | F.col(fail_cols[4]) | F.col(fail_cols[5]),
        )

        # ── 9. Single-pass aggregation of all check counts ────
        agg_row = df.select(
            *[F.sum(F.col(c).cast("int")).alias(c) for c in fail_cols],
        ).collect()[0]
        metrics.null_count = int(agg_row["__null_fail"] or 0)
        metrics.duplicate_count = int(agg_row["__dup_fail"] or 0)
        metrics.invalid_vin_count = int(agg_row["__vin_fail"] or 0)
        metrics.invalid_date_count = int(agg_row["__date_fail"] or 0)
        metrics.range_violation_count = int(agg_row["__range_fail"] or 0)
        metrics.referential_error_count = int(agg_row["__ref_fail"] or 0)

        self.logger.info(f"Null issues: {metrics.null_count:,}")
        self.logger.info(f"Duplicate records: {metrics.duplicate_count:,}")
        self.logger.info(f"Invalid VIN: {metrics.invalid_vin_count:,}")
        self.logger.info(f"Invalid dates: {metrics.invalid_date_count:,}")
        self.logger.info(f"Range violations: {metrics.range_violation_count:,}")
        self.logger.info(f"Referential errors: {metrics.referential_error_count:,}")

        # ── 10. Build error description for quarantine ─────────
        df = df.withColumn(
            "__error_types",
            F.concat_ws(
                "|",
                F.when(F.col("__null_fail"), F.lit(ERROR_NULL)),
                F.when(F.col("__dup_fail"), F.lit(ERROR_DUPLICATE)),
                F.when(F.col("__vin_fail"), F.lit(ERROR_VIN)),
                F.when(F.col("__date_fail"), F.lit(ERROR_DATE)),
                F.when(F.col("__range_fail"), F.lit(ERROR_RANGE)),
                F.when(F.col("__ref_fail"), F.lit(ERROR_REFERENTIAL)),
            ),
        )
        df = df.withColumn(
            "__error_messages",
            F.concat_ws(
                " | ",
                F.when(F.col("__null_fail"), F.concat(F.lit("Null values in: "), F.col("__null_cols"))),
                F.when(F.col("__dup_fail"), F.lit("Duplicate record detected")),
                F.when(F.col("__vin_fail"), F.lit("Invalid or missing VIN")),
                F.when(F.col("__date_fail"), F.concat(F.lit("Invalid date in: "), F.col("__date_cols"))),
                F.when(F.col("__range_fail"), F.concat(F.lit("Out-of-range value in: "), F.col("__range_cols"))),
                F.when(F.col("__ref_fail"), F.lit("Referential integrity violation")),
            ),
        )

        # ── 11. Split valid / invalid ─────────────────────────
        internal_cols = [c for c in df.columns if c.startswith("__")]
        valid_df = df.filter(~F.col("__any_fail")).drop(*internal_cols)
        invalid_df = df.filter(F.col("__any_fail"))

        metrics.rejected_records = invalid_df.count()
        metrics.valid_records = total - metrics.rejected_records
        metrics.duration_seconds = round(time.time() - start, 3)

        self.logger.records_processed(total)
        self.logger.valid_records(metrics.valid_records)
        self.logger.rejected_records(metrics.rejected_records)

        return valid_df, invalid_df, metrics
