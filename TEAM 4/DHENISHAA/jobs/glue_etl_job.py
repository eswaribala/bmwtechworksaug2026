"""Glue ETL job entry point for processing BMW telemetry and supporting datasets.

This script is intentionally self-contained so it can run inside AWS Glue without
requiring the local project package to be deployed alongside it.
"""

from __future__ import annotations

import argparse
import logging

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("glue_etl_job")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Process BMW telemetry in the AWS data lake.")
    parser.add_argument("--bucket", default="bmw-serverless-data-lake-dev-bmw-data-lake-dev", help="S3 bucket name")
    parser.add_argument("--raw-prefix", default="raw", help="Raw input prefix inside the bucket")
    parser.add_argument("--output-prefix", default="curated/telemetry", help="Curated output prefix inside the bucket")
    return parser.parse_known_args()[0]


def main() -> None:
    """Entry point for the Glue ETL job."""
    args = parse_args()

    spark = SparkSession.builder.appName("bmw-serverless-data-lake-etl").getOrCreate()
    logger.info("Spark session started.")

    input_path = f"s3://{args.bucket}/{args.raw_prefix}/"
    output_path = f"s3://{args.bucket}/{args.output_prefix}/"

    telemetry = spark.read.option("header", True).csv(input_path + "telemetry.csv")
    telemetry = telemetry.withColumn("year", F.col("year").cast("int"))
    telemetry = telemetry.withColumn("month", F.col("month").cast("int"))
    telemetry = telemetry.withColumn("battery_level", F.col("battery_level").cast("double"))
    telemetry = telemetry.withColumn("battery_temperature", F.col("battery_temperature").cast("double"))
    telemetry = telemetry.withColumn("event_timestamp", F.to_timestamp("event_timestamp"))

    telemetry.write.mode("overwrite").partitionBy("year", "month").parquet(output_path)
    logger.info("Telemetry data written to %s", output_path)

    spark.stop()


if __name__ == "__main__":
    main()
