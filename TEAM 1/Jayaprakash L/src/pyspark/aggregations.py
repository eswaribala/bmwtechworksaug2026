"""PySpark aggregation functions for the analytics data layer.

The functions convert event-level telemetry into vehicle, model, region,
and daily range-trend datasets suitable for Parquet, Athena, or dashboards.
"""

from pyspark.sql import functions as F

def vehicle_efficiency(df):
    """Aggregate event telemetry into one record per vehicle/model/region."""
    return (
        df.groupBy("vehicle_id","model","region")
        .agg(
            F.sum("distance_km").alias("total_distance_km"),
            F.sum(
                F.when(F.col("battery_consumed") > 0,
                       F.col("battery_consumed")).otherwise(0)
            ).alias("total_battery_consumed"),
            F.avg("speed_kmh").alias("avg_speed_kmh"),
            F.avg("temperature_c").alias("avg_temperature_c"),
            F.avg("estimated_range_km").alias("avg_estimated_range_km")
        )
        .withColumn(
            "overall_efficiency",
            F.when(
                F.col("total_battery_consumed") > 0,
                F.col("total_distance_km") /
                F.col("total_battery_consumed")
            )
        )
    )

def model_efficiency(df):
    """Aggregate vehicle metrics into model-level efficiency metrics."""
    return (
        vehicle_efficiency(df)
        .groupBy("model")
        .agg(
            F.sum("total_distance_km").alias("total_distance_km"),
            F.sum("total_battery_consumed").alias("total_battery_consumed")
        )
        .withColumn(
            "overall_efficiency",
            F.col("total_distance_km") /
            F.col("total_battery_consumed")
        )
    )

def region_efficiency(df):
    """Aggregate vehicle metrics into region-level efficiency metrics."""
    return (
        vehicle_efficiency(df)
        .groupBy("region")
        .agg(
            F.sum("total_distance_km").alias("total_distance_km"),
            F.sum("total_battery_consumed").alias("total_battery_consumed")
        )
        .withColumn(
            "overall_efficiency",
            F.col("total_distance_km") /
            F.col("total_battery_consumed")
        )
    )

def range_trend(df):
    """Aggregate estimated range and battery level by calendar date."""
    return (
        df.withColumn("date", F.to_date("timestamp"))
        .groupBy("date")
        .agg(
            F.avg("estimated_range_km").alias("avg_estimated_range_km"),
            F.avg("battery_percent").alias("avg_battery_percent")
        )
        .orderBy("date")
    )
