"""
BMW Data Quality & Governance Platform — Quality Engine
Participant 12 | Pod D
Orchestrates all validators, routes records to valid/invalid partitions.
"""

import pandas as pd
from datetime import datetime, timezone
from typing import Optional
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
    Main orchestrator — runs all validation checks and separates
    valid records (curated) from invalid records (quarantine).
    """

    def __init__(self, dataset: str, logger: Optional[BmwLogger] = None):
        self.dataset = dataset
        self.logger = logger or BmwLogger(dataset)

    def run(
        self,
        df: pd.DataFrame,
        reference_df: Optional[pd.DataFrame] = None,
    ) -> tuple[pd.DataFrame, pd.DataFrame, QualityMetrics]:
        """
        Execute the full quality pipeline on df.

        Args:
            df:           Input raw DataFrame.
            reference_df: Vehicle master for referential integrity checks.

        Returns:
            (valid_df, invalid_df, metrics)
        """
        import time
        start = time.time()

        total = len(df)
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
        metrics.null_count = int(df["__null_fail"].sum())
        metrics.null_summary = null_summary(df, self.dataset)
        self.logger.info(f"Null issues: {metrics.null_count:,}")

        # ── 3. Duplicate check ────────────────────────────────
        df = check_duplicates(df, self.dataset)
        metrics.duplicate_count = int(df["__dup_fail"].sum())
        self.logger.info(f"Duplicate records: {metrics.duplicate_count:,}")

        # ── 4. VIN check ──────────────────────────────────────
        df = check_vin(df)
        metrics.invalid_vin_count = int(df["__vin_fail"].sum())
        self.logger.info(f"Invalid VIN: {metrics.invalid_vin_count:,}")

        # ── 5. Date check ─────────────────────────────────────
        df = check_dates(df, self.dataset)
        metrics.invalid_date_count = int(df["__date_fail"].sum())
        self.logger.info(f"Invalid dates: {metrics.invalid_date_count:,}")

        # ── 6. Range check ────────────────────────────────────
        df = check_ranges(df)
        metrics.range_violation_count = int(df["__range_fail"].sum())
        self.logger.info(f"Range violations: {metrics.range_violation_count:,}")

        # ── 7. Referential integrity ──────────────────────────
        if reference_df is not None and self.dataset in REFERENTIAL_RULES:
            fk_col, _parent, pk_col = REFERENTIAL_RULES[self.dataset]
            df = check_referential_integrity(df, fk_col, reference_df, pk_col)
            metrics.referential_error_count = int(df["__ref_fail"].sum())
            self.logger.info(f"Referential errors: {metrics.referential_error_count:,}")
        else:
            df["__ref_fail"] = False

        # ── 8. Combine failure flags ──────────────────────────
        fail_cols = [
            "__null_fail", "__dup_fail", "__vin_fail",
            "__date_fail", "__range_fail", "__ref_fail",
        ]
        df["__any_fail"] = df[fail_cols].any(axis=1)

        # ── 9. Build error description for quarantine ─────────
        df["__error_types"] = df.apply(self._build_error_types, axis=1)
        df["__error_messages"] = df.apply(self._build_error_messages, axis=1)

        # ── 10. Split valid / invalid ─────────────────────────
        internal_cols = [c for c in df.columns if c.startswith("__")]
        valid_df = df[~df["__any_fail"]].drop(columns=internal_cols).reset_index(drop=True)
        invalid_df = df[df["__any_fail"]].copy().reset_index(drop=True)

        metrics.valid_records = len(valid_df)
        metrics.rejected_records = len(invalid_df)
        metrics.duration_seconds = round(time.time() - start, 3)

        self.logger.records_processed(total)
        self.logger.valid_records(metrics.valid_records)
        self.logger.rejected_records(metrics.rejected_records)

        return valid_df, invalid_df, metrics

    # ──────────────────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────────────────

    def _build_error_types(self, row: pd.Series) -> str:
        types = []
        if row.get("__null_fail"):
            types.append(ERROR_NULL)
        if row.get("__dup_fail"):
            types.append(ERROR_DUPLICATE)
        if row.get("__vin_fail"):
            types.append(ERROR_VIN)
        if row.get("__date_fail"):
            types.append(ERROR_DATE)
        if row.get("__range_fail"):
            types.append(ERROR_RANGE)
        if row.get("__ref_fail"):
            types.append(ERROR_REFERENTIAL)
        return "|".join(types)

    def _build_error_messages(self, row: pd.Series) -> str:
        msgs = []
        if row.get("__null_fail"):
            cols = row.get("__null_cols", "")
            msgs.append(f"Null values in: {cols}")
        if row.get("__dup_fail"):
            msgs.append("Duplicate record detected")
        if row.get("__vin_fail"):
            msgs.append("Invalid or missing VIN")
        if row.get("__date_fail"):
            cols = row.get("__date_cols", "")
            msgs.append(f"Invalid date in: {cols}")
        if row.get("__range_fail"):
            cols = row.get("__range_cols", "")
            msgs.append(f"Out-of-range value in: {cols}")
        if row.get("__ref_fail"):
            msgs.append("Referential integrity violation")
        return " | ".join(msgs)
