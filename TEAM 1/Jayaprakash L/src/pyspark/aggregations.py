from pyspark.sql import functions as F

def vehicle_efficiency(df):
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
    return (
        df.withColumn("date", F.to_date("timestamp"))
        .groupBy("date")
        .agg(
            F.avg("estimated_range_km").alias("avg_estimated_range_km"),
            F.avg("battery_percent").alias("avg_battery_percent")
        )
        .orderBy("date")
    )
