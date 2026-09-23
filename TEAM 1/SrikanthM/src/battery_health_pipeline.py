from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame, functions as F


def write_parquet_to_s3(df: DataFrame, s3_path: str) -> None:
    """Write a Spark Parquet dataset locally, then upload its files to S3."""
    parsed_path = urlparse(s3_path)
    if parsed_path.scheme not in {"s3", "s3a"} or not parsed_path.netloc:
        raise ValueError("CURATED_S3_PATH must use s3:// or s3a:// and include a bucket")

    bucket = parsed_path.netloc
    prefix = parsed_path.path.strip("/")
    temporary_dir = Path(tempfile.mkdtemp(prefix="ev_battery_health_"))

    try:
        pandas_df = df.toPandas()
        for category, category_df in pandas_df.groupby(
            "battery_health_category", dropna=False
        ):
            category_name = str(category)
            category_dir = temporary_dir / (
                f"battery_health_category={category_name}"
            )
            category_dir.mkdir(parents=True, exist_ok=True)
            category_df.to_parquet(
                category_dir / "part-00000.parquet",
                index=False,
            )

        s3_client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION"),
        )
        try:
            s3_client.head_bucket(Bucket=bucket)
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code", "Unknown")
            raise RuntimeError(
                f"Cannot access S3 bucket '{bucket}' ({error_code}). "
                "Confirm the bucket exists in the active AWS account and region, "
                "then verify AWS_PROFILE/AWS_REGION."
            ) from error

        paginator = s3_client.get_paginator("list_objects_v2")
        existing_objects = []
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            existing_objects.extend(
                {"Key": item["Key"]} for item in page.get("Contents", [])
            )

        for start in range(0, len(existing_objects), 1000):
            s3_client.delete_objects(
                Bucket=bucket,
                Delete={"Objects": existing_objects[start : start + 1000]},
            )

        for parquet_file in temporary_dir.rglob("*.parquet"):
            relative_path = parquet_file.relative_to(temporary_dir).as_posix()
            object_key = f"{prefix}/{relative_path}"
            s3_client.upload_file(str(parquet_file), bucket, object_key)
    finally:
        shutil.rmtree(temporary_dir, ignore_errors=True)


def build_ev_battery_health_pipeline(data_dir: str | Path) -> DataFrame:
    """Build the EV battery health dataset and classify each vehicle."""
    configured_python = os.getenv("PYSPARK_PYTHON")
    if configured_python and not Path(configured_python).exists():
        os.environ["PYSPARK_PYTHON"] = sys.executable

    configured_driver_python = os.getenv("PYSPARK_DRIVER_PYTHON")
    if configured_driver_python and not Path(configured_driver_python).exists():
        os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    read_from_s3 = os.getenv("READ_RAW_FROM_S3", "true").lower() in {
        "1",
        "true",
        "yes",
    }
    write_to_s3 = os.getenv("WRITE_CURATED_TO_S3", "true").lower() in {
        "1",
        "true",
        "yes",
    }

    spark = (
        SparkSession.builder
        .appName("EV_Battery_Health_Intelligence")
        .master("local[*]")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
    )

    if read_from_s3:
        raw_s3_path = os.getenv(
            "RAW_S3_PATH",
            "s3a://ev-battery-health-data/raw",
        )
        spark = (
            spark
            .config(
                "spark.jars.packages",
                "org.apache.hadoop:hadoop-aws:3.5.0",
            )
            .config(
                "spark.hadoop.fs.s3a.aws.credentials.provider",
                "software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider",
            )
            .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
            .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000")
            .config("spark.hadoop.fs.s3a.connection.request.timeout", "60000")
            .config("spark.hadoop.fs.s3a.socket.timeout", "60000")
            .getOrCreate()
        )
        base_path = raw_s3_path.rstrip("/")
        print(f"Reading raw data directly from {raw_s3_path}")
    else:
        spark = spark.getOrCreate()
        base_path = Path(data_dir)

    def input_path(filename: str) -> str:
        if isinstance(base_path, Path):
            return str(base_path / filename)
        dataset_name = Path(filename).stem
        return f"{base_path}/{dataset_name}/{filename}"

    telemetry_df = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(input_path("telemetry.csv"))
    )

    vehicle_master_df = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(input_path("vehicle_master.csv"))
    )

    charging_df = (
        spark.read.option("header", True)
        .option("inferSchema", True)
        .csv(input_path("charging_sessions.csv"))
    )

    telemetry_df = (
        telemetry_df
        .withColumn("Timestamp", F.to_timestamp("Timestamp", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("SoC_Percent", F.col("SoC_Percent").cast("double"))
        .withColumn("SoH_Percent", F.col("SoH_Percent").cast("double"))
        .withColumn("Battery_Voltage_V", F.col("Battery_Voltage_V").cast("double"))
        .withColumn("Battery_Current_A", F.col("Battery_Current_A").cast("double"))
        .withColumn("Battery_Temperature_C", F.col("Battery_Temperature_C").cast("double"))
        .withColumn("Charging_Power_kW", F.col("Charging_Power_kW").cast("double"))
        .withColumn("Vehicle_Speed_kmh", F.col("Vehicle_Speed_kmh").cast("double"))
        .withColumn("Odometer_km", F.col("Odometer_km").cast("double"))
        .na.drop(subset=["Vehicle_ID", "Timestamp", "SoH_Percent"])
    )

    vehicle_master_df = (
        vehicle_master_df
        .withColumn("Model_Year", F.col("Model_Year").cast("int"))
        .withColumn("Battery_Capacity_kWh", F.col("Battery_Capacity_kWh").cast("double"))
        .withColumn("Vehicle_Age_Years", F.col("Vehicle_Age_Years").cast("int"))
        .withColumn("Odometer_km", F.col("Odometer_km").cast("double"))
        .na.drop(subset=["Vehicle_ID", "Model", "Region"])
    )

    charging_df = (
        charging_df
        .withColumn("Session_Start", F.to_timestamp("Session_Start", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("Session_End", F.to_timestamp("Session_End", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("Energy_Delivered_kWh", F.col("Energy_Delivered_kWh").cast("double"))
        .withColumn("Initial_SoC_Percent", F.col("Initial_SoC_Percent").cast("double"))
        .withColumn("Final_SoC_Percent", F.col("Final_SoC_Percent").cast("double"))
        .withColumn("Charging_Duration_Min", F.col("Charging_Duration_Min").cast("double"))
        .withColumn("Charging_Power_kW", F.col("Charging_Power_kW").cast("double"))
        .withColumn("Charging_Interruptions", F.col("Charging_Interruptions").cast("int"))
        .withColumn("Charger_Temperature_C", F.col("Charger_Temperature_C").cast("double"))
        .withColumn("Environment_Temperature_C", F.col("Environment_Temperature_C").cast("double"))
        .na.drop(subset=["Vehicle_ID", "Session_Start", "Session_End"])
    )

    vehicle_metrics = (
        telemetry_df.groupBy("Vehicle_ID")
        .agg(
            F.avg("SoC_Percent").alias("avg_battery_level"),
            F.avg("SoH_Percent").alias("avg_soh"),
            F.min("SoH_Percent").alias("min_soh"),
            F.max("SoH_Percent").alias("max_soh"),
            F.stddev("SoH_Percent").alias("soh_stddev"),
            F.count("*").alias("telemetry_records"),
            F.first("Timestamp").alias("first_seen"),
            F.last("Timestamp").alias("last_seen"),
        )
    )

    degradation_trend = (
        telemetry_df.orderBy("Vehicle_ID", "Timestamp")
        .groupBy("Vehicle_ID")
        .agg(
            F.first("SoH_Percent").alias("initial_soh"),
            F.last("SoH_Percent").alias("latest_soh"),
            (F.last("SoH_Percent") - F.first("SoH_Percent")).alias("soh_drop"),
            (
                (F.last("SoH_Percent") - F.first("SoH_Percent"))
                / F.first("SoH_Percent")
                * 100
            ).alias("percent_drop"),
        )
    )

    charging_metrics = (
        charging_df.groupBy("Vehicle_ID")
        .agg(
            F.count("*").alias("charging_frequency"),
            F.avg("Energy_Delivered_kWh").alias("avg_energy_delivered_kwh"),
            F.avg("Charging_Power_kW").alias("avg_charging_power_kw"),
            F.avg("Charging_Duration_Min").alias("avg_charging_duration_min"),
            F.sum(F.when(F.col("Charging_Interruptions") > 0, 1).otherwise(0)).alias(
                "charging_interruptions_count"
            ),
        )
    )

    final_df = (
        vehicle_metrics
        .join(vehicle_master_df, on="Vehicle_ID", how="left")
        .join(charging_metrics, on="Vehicle_ID", how="left")
        .join(degradation_trend, on="Vehicle_ID", how="left")
    )

    final_df = (
        final_df
        .withColumn(
            "battery_health_category",
            F.when(F.col("avg_soh") >= 90, "Healthy")
            .when(F.col("avg_soh") >= 80, "Watch")
            .otherwise("Critical"),
        )
        .withColumn(
            "health_score",
            F.when(F.col("avg_soh") >= 90, 100)
            .when(F.col("avg_soh") >= 80, 70)
            .otherwise(40),
        )
    )

    final_df = (
        final_df.withColumn(
            "battery_health_category",
            F.when(
                (F.col("battery_health_category") == "Healthy")
                & (F.col("percent_drop") > 10),
                "Watch",
            )
            .when(
                (F.col("battery_health_category") == "Watch")
                & (F.col("percent_drop") > 15),
                "Critical",
            )
            .otherwise(F.col("battery_health_category")),
        )
    )

    if write_to_s3:
        curated_path = os.getenv(
            "CURATED_S3_PATH",
            "s3a://ev-battery-health-data/curated/vehicle_health",
        )
        write_parquet_to_s3(final_df, curated_path)
        print(f"Curated vehicle health data written to {curated_path}")

    return final_df


if __name__ == "__main__":
    result = build_ev_battery_health_pipeline("src/datas")
    try:
        result.show(20, truncate=False)
        result.select(
            "Vehicle_ID",
            "Model",
            "Region",
            "avg_soh",
            "charging_frequency",
            "soh_drop",
            "battery_health_category",
        ).show(20, truncate=False)
    finally:
        result.sparkSession.stop()