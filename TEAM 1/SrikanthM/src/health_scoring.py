from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def classify_battery_health(df: DataFrame) -> DataFrame:
    """Assign health categories based on thresholds."""
    return (
        df.withColumn(
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


def calculate_degradation_trend(df: DataFrame) -> DataFrame:
    """Estimate battery degradation trend using SoH slope across time."""
    return (
        df.orderBy("Vehicle_ID", "Timestamp")
        .groupBy("Vehicle_ID")
        .agg(
            F.avg("SoH_Percent").alias("avg_soh"),
            F.min("SoH_Percent").alias("min_soh"),
            F.max("SoH_Percent").alias("max_soh"),
            F.stddev("SoH_Percent").alias("soh_stddev"),
        )
    )
