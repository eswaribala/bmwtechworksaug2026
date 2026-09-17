"""
BMW Data Quality & Governance Platform — Quarantine
Participant 12 | Pod D
Annotates invalid records with PySpark; materialised to pandas only at the
final single-file CSV/Parquet write boundary.
"""

from datetime import datetime, timezone
from typing import Optional
from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from src.utils.logger import BmwLogger


class QuarantineManager:
    """
    Takes invalid records produced by QualityEngine and enriches them
    with error metadata before writing to the quarantine S3 zone.
    """

    def __init__(self, dataset: str, logger: Optional[BmwLogger] = None):
        self.dataset = dataset
        self.logger = logger or BmwLogger(f"{dataset}_quarantine")

    def prepare(self, invalid_df: DataFrame) -> DataFrame:
        """
        Enrich invalid records with quarantine metadata columns.

        Added columns:
            quarantine_dataset        — source dataset name
            quarantine_error_type     — pipe-separated error type codes
            quarantine_error_message  — human-readable error description
            quarantine_validation_rule — same as error_type (for reference)
            quarantine_timestamp      — ISO 8601 processing timestamp
        """
        ts = datetime.now(timezone.utc).isoformat()
        cols = invalid_df.columns
        error_type_expr = F.col("__error_types") if "__error_types" in cols else F.lit("UNKNOWN")
        error_msg_expr = F.col("__error_messages") if "__error_messages" in cols else F.lit("")

        df = (
            invalid_df
            .withColumn("quarantine_dataset", F.lit(self.dataset))
            .withColumn("quarantine_error_type", error_type_expr)
            .withColumn("quarantine_error_message", error_msg_expr)
            .withColumn("quarantine_validation_rule", error_type_expr)
            .withColumn("quarantine_timestamp", F.lit(ts))
        )

        # Drop internal processing columns
        internal_cols = [c for c in df.columns if c.startswith("__")]
        df = df.drop(*internal_cols)

        self.logger.info(f"Prepared {df.count():,} records for quarantine")
        return df

    def save(
        self,
        invalid_df: DataFrame,
        output_path: str,
        fmt: str = "csv",
    ) -> str:
        """
        Save quarantine records to the given path.

        Args:
            invalid_df:  Spark DataFrame already enriched by prepare().
            output_path: Local directory path or S3 key prefix.
            fmt:         'csv' or 'parquet'.

        Returns:
            Path or S3 key where records were written.
        """
        from pathlib import Path

        ts_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"quarantine_{self.dataset}_{ts_str}.{fmt}"

        # Materialise to pandas for a single named output file
        pdf = invalid_df.toPandas()

        if output_path.startswith("s3://"):
            # S3 path — delegate to s3_loader
            from src.ingestion.s3_loader import S3Loader
            parts = output_path[5:].split("/", 1)
            bucket = parts[0]
            prefix = parts[1] if len(parts) > 1 else ""
            key = f"{prefix}/{filename}".lstrip("/")
            loader = S3Loader(bucket, self.logger)
            if fmt == "parquet":
                return loader.write_parquet(pdf, key)
            return loader.write_csv(pdf, key)
        else:
            # Local filesystem
            path = Path(output_path) / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            if fmt == "parquet":
                pdf.to_parquet(path, index=False)
            else:
                pdf.to_csv(path, index=False)
            self.logger.info(f"Quarantine saved: {path}")
            return str(path)

    def sample_records(self, quarantine_df: DataFrame, n: int = 5) -> list[dict]:
        """Return n sample quarantine records as dicts (for reporting)."""
        return [row.asDict() for row in quarantine_df.limit(n).collect()]
