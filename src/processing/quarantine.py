"""
BMW Data Quality & Governance Platform — Quarantine
Participant 12 | Pod D
Annotates and persists invalid records to the quarantine zone.
"""

import pandas as pd
from datetime import datetime, timezone
from typing import Optional
from src.utils.logger import BmwLogger


class QuarantineManager:
    """
    Takes invalid records produced by QualityEngine and enriches them
    with error metadata before writing to the quarantine S3 zone.
    """

    def __init__(self, dataset: str, logger: Optional[BmwLogger] = None):
        self.dataset = dataset
        self.logger = logger or BmwLogger(f"{dataset}_quarantine")

    def prepare(self, invalid_df: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich invalid records with quarantine metadata columns.

        Added columns:
            quarantine_dataset        — source dataset name
            quarantine_error_type     — pipe-separated error type codes
            quarantine_error_message  — human-readable error description
            quarantine_validation_rule — same as error_type (for reference)
            quarantine_timestamp      — ISO 8601 processing timestamp
        """
        df = invalid_df.copy()
        ts = datetime.now(timezone.utc).isoformat()

        # Map internal columns to quarantine metadata
        df["quarantine_dataset"] = self.dataset
        df["quarantine_error_type"] = df.get("__error_types", "UNKNOWN")
        df["quarantine_error_message"] = df.get("__error_messages", "")
        df["quarantine_validation_rule"] = df.get("__error_types", "UNKNOWN")
        df["quarantine_timestamp"] = ts

        # Drop internal processing columns
        internal_cols = [c for c in df.columns if c.startswith("__")]
        df = df.drop(columns=internal_cols, errors="ignore")

        self.logger.info(f"Prepared {len(df):,} records for quarantine")
        return df

    def save(
        self,
        invalid_df: pd.DataFrame,
        output_path: str,
        fmt: str = "csv",
    ) -> str:
        """
        Save quarantine records to the given path.

        Args:
            invalid_df:  DataFrame already enriched by prepare().
            output_path: Local directory path or S3 key prefix.
            fmt:         'csv' or 'parquet'.

        Returns:
            Path or S3 key where records were written.
        """
        import os
        from pathlib import Path

        ts_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"quarantine_{self.dataset}_{ts_str}.{fmt}"

        if output_path.startswith("s3://"):
            # S3 path — delegate to s3_loader
            from src.ingestion.s3_loader import S3Loader
            parts = output_path[5:].split("/", 1)
            bucket = parts[0]
            prefix = parts[1] if len(parts) > 1 else ""
            key = f"{prefix}/{filename}".lstrip("/")
            loader = S3Loader(bucket, self.logger)
            if fmt == "parquet":
                return loader.write_parquet(invalid_df, key)
            return loader.write_csv(invalid_df, key)
        else:
            # Local filesystem
            path = Path(output_path) / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            if fmt == "parquet":
                invalid_df.to_parquet(path, index=False)
            else:
                invalid_df.to_csv(path, index=False)
            self.logger.info(f"Quarantine saved: {path}")
            return str(path)

    def sample_records(self, quarantine_df: pd.DataFrame, n: int = 5) -> list[dict]:
        """Return n sample quarantine records as dicts (for reporting)."""
        return quarantine_df.head(n).to_dict(orient="records")
