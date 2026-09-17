"""
BMW Data Quality & Governance Platform — S3 Loader
Participant 12 | Pod D
Loads datasets from S3 or local filesystem into PySpark DataFrames for
processing. Metadata (JSON) and reference lookups still use pandas/boto3
directly since they are not part of the distributed processing path.
"""

import os
import json
import pandas as pd
from pathlib import Path
from typing import Optional
from src.utils.logger import BmwLogger
from src.utils.spark_session import get_spark


class S3Loader:
    """
    Loads BMW datasets from Amazon S3 or a local path.
    When AWS credentials are not configured the loader uses the local filesystem.
    """

    def __init__(self, bucket: str, logger: Optional[BmwLogger] = None):
        self.bucket = bucket
        self.logger = logger or BmwLogger("s3_loader")
        self._s3_client = None

    def _get_s3_client(self):
        """Lazily initialise the boto3 S3 client."""
        if self._s3_client is None:
            try:
                import boto3
                self._s3_client = boto3.client("s3")
            except Exception as exc:
                self.logger.warn(f"boto3 not available or credentials missing: {exc}")
        return self._s3_client

    # ──────────────────────────────────────────────────
    # PySpark-backed loading (used by the quality engine)
    # ──────────────────────────────────────────────────

    def load_csv_spark(self, key: str, local_path: Optional[str] = None):
        """
        Load a CSV file into a PySpark DataFrame.

        Tries the local path first; otherwise downloads the object bytes
        from S3 via boto3 into a temp file and reads that with Spark
        (S3 transport stays on boto3; distributed processing uses Spark).
        """
        spark = get_spark()

        if local_path and os.path.exists(local_path):
            self.logger.info(f"Loading CSV (Spark) from local path: {local_path}")
            return spark.read.option("header", True).option("inferSchema", True).csv(local_path)

        client = self._get_s3_client()
        if client:
            import tempfile
            self.logger.info(f"Loading CSV (Spark) from s3://{self.bucket}/{key}")
            try:
                obj = client.get_object(Bucket=self.bucket, Key=key)
                with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                    tmp.write(obj["Body"].read())
                    tmp_path = tmp.name
                return spark.read.option("header", True).option("inferSchema", True).csv(tmp_path)
            except Exception as exc:
                self.logger.error(f"S3 load failed: {exc}")
                raise

        raise FileNotFoundError(
            f"Could not load data. S3 unavailable and no local path provided for key={key}"
        )

    # ──────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────

    def load_csv(self, key: str, local_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load a CSV file.  Tries S3 first; falls back to local path.

        Args:
            key:        S3 object key (e.g. 'raw/telemetry/telemetry.csv')
            local_path: Absolute or relative local path used as fallback.

        Returns:
            pandas DataFrame
        """
        if local_path and os.path.exists(local_path):
            self.logger.info(f"Loading CSV from local path: {local_path}")
            return pd.read_csv(local_path)

        client = self._get_s3_client()
        if client:
            try:
                self.logger.info(f"Loading CSV from s3://{self.bucket}/{key}")
                obj = client.get_object(Bucket=self.bucket, Key=key)
                return pd.read_csv(obj["Body"])
            except Exception as exc:
                self.logger.error(f"S3 load failed: {exc}")
                raise

        raise FileNotFoundError(
            f"Could not load data. S3 unavailable and no local path provided for key={key}"
        )

    def load_parquet(self, key: str, local_path: Optional[str] = None) -> pd.DataFrame:
        """Load a Parquet file from S3 or local path."""
        if local_path and os.path.exists(local_path):
            self.logger.info(f"Loading Parquet from local path: {local_path}")
            return pd.read_parquet(local_path)

        client = self._get_s3_client()
        if client:
            try:
                import io
                self.logger.info(f"Loading Parquet from s3://{self.bucket}/{key}")
                obj = client.get_object(Bucket=self.bucket, Key=key)
                return pd.read_parquet(io.BytesIO(obj["Body"].read()))
            except Exception as exc:
                self.logger.error(f"S3 Parquet load failed: {exc}")
                raise

        raise FileNotFoundError(f"Could not load Parquet. key={key}")

    def write_csv(self, df: pd.DataFrame, key: str, local_dir: Optional[str] = None) -> str:
        """Write DataFrame as CSV to S3 or local directory."""
        if local_dir:
            path = Path(local_dir) / Path(key).name
            path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(path, index=False)
            self.logger.info(f"Written CSV locally: {path}")
            return str(path)

        client = self._get_s3_client()
        if client:
            import io
            buf = io.StringIO()
            df.to_csv(buf, index=False)
            client.put_object(Bucket=self.bucket, Key=key, Body=buf.getvalue())
            self.logger.info(f"Written CSV to s3://{self.bucket}/{key}")
            return f"s3://{self.bucket}/{key}"

        raise RuntimeError("No write destination available.")

    def write_parquet(self, df: pd.DataFrame, key: str, local_dir: Optional[str] = None) -> str:
        """Write DataFrame as Parquet to S3 or local directory."""
        if local_dir:
            path = Path(local_dir) / Path(key).name
            path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(path, index=False)
            self.logger.info(f"Written Parquet locally: {path}")
            return str(path)

        client = self._get_s3_client()
        if client:
            import io
            buf = io.BytesIO()
            df.to_parquet(buf, index=False)
            buf.seek(0)
            client.put_object(Bucket=self.bucket, Key=key, Body=buf.read())
            self.logger.info(f"Written Parquet to s3://{self.bucket}/{key}")
            return f"s3://{self.bucket}/{key}"

        raise RuntimeError("No write destination available.")

    def write_json(self, data: dict | list, key: str, local_dir: Optional[str] = None) -> str:
        """Write JSON to S3 or local directory."""
        payload = json.dumps(data, indent=2, default=str)

        if local_dir:
            path = Path(local_dir) / Path(key).name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(payload, encoding="utf-8")
            self.logger.info(f"Written JSON locally: {path}")
            return str(path)

        client = self._get_s3_client()
        if client:
            client.put_object(Bucket=self.bucket, Key=key, Body=payload)
            self.logger.info(f"Written JSON to s3://{self.bucket}/{key}")
            return f"s3://{self.bucket}/{key}"

        raise RuntimeError("No write destination available.")
