from pyspark.sql import functions as F
from pyspark.sql.window import Window

def transform_telemetry(df):
    df = df.dropna(subset=[
        "vehicle_id","model","region","timestamp",
        "speed_kmh","battery_percent","distance_km"
    ])

    df = df.filter(
        (F.col("speed_kmh") >= 0) &
        (F.col("distance_km") > 0) &
        F.col("battery_percent").between(0,100)
    )

    # Window function: previous battery for each vehicle.
    w = Window.partitionBy("vehicle_id").orderBy("timestamp")

    df = df.withColumn(
        "previous_battery",
        F.lag("battery_percent").over(w)
    )

    df = df.withColumn(
        "battery_consumed",
        F.col("previous_battery") - F.col("battery_percent")
    )

    df = df.withColumn(
        "event_efficiency",
        F.when(
            F.col("battery_consumed") > 0,
            F.col("distance_km") / F.col("battery_consumed")
        )
    )

    df = df.withColumn(
        "estimated_range_km",
        F.when(
            F.col("event_efficiency") > 0,
            F.col("battery_percent") * F.col("event_efficiency")
        )
    )

    return df
