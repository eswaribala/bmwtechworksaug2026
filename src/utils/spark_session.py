"""
BMW Data Quality & Governance Platform — Spark Session Factory
Participant 12 | Pod D

Provides a single shared local SparkSession used by the CLI, backend API,
and test suite for all PySpark-based data quality processing.
"""

import os
import sys

# Ensure Spark's Python workers use the same interpreter as the driver.
os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

from pyspark.sql import SparkSession

_spark: SparkSession | None = None


def get_spark(app_name: str = "bmw-data-quality") -> SparkSession:
    """Return the shared local SparkSession, creating it on first use."""
    global _spark
    if _spark is None:
        _spark = (
            SparkSession.builder
            .appName(app_name)
            .master(os.getenv("SPARK_MASTER", "local[2]"))
            .config("spark.ui.showConsoleProgress", "false")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "8")
            .config("spark.driver.memory", os.getenv("SPARK_DRIVER_MEMORY", "2g"))
            .getOrCreate()
        )
        _spark.sparkContext.setLogLevel("WARN")
    return _spark


def stop_spark() -> None:
    """Stop the shared SparkSession, if running."""
    global _spark
    if _spark is not None:
        _spark.stop()
        _spark = None
