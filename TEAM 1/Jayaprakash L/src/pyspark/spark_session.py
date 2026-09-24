"""Spark session configuration for local EV analytics.

The project uses a local Spark session for development and testing. The
same transformation functions can be reused by an AWS Glue Spark job.
"""

from pyspark.sql import SparkSession

def create_spark(app_name="EV-Range-Analytics"):
    """Create and configure the Spark session used by local analytics."""
    return (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions","4")
        .getOrCreate()
    )
