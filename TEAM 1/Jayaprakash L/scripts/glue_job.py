"""AWS Glue Spark job for the production analytics pipeline.

Inputs
------
input_path:
    S3 URI containing the raw telemetry CSV.
output_path:
    S3 URI under which curated Parquet datasets are written.

The job cleans telemetry, calculates battery consumption and estimated
range, aggregates vehicle/model/region metrics, and writes analytics
datasets for the Glue Catalog and Athena.
"""

# AWS Glue 4.0/5.0 Spark job
# Job parameters:
# --input_path s3://YOUR-BUCKET/raw/vehicles/dataset.csv
# --output_path s3://YOUR-BUCKET/curated

import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window

args = getResolvedOptions(sys.argv, ["input_path","output_path"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

df = (
    spark.read.option("header",True)
    .option("inferSchema",True)
    .csv(args["input_path"])
)

df = df.dropna(subset=[
    "vehicle_id","model","region","timestamp",
    "speed_kmh","battery_percent","distance_km"
])

df = df.filter(
    (F.col("speed_kmh") >= 0) &
    (F.col("distance_km") > 0) &
    F.col("battery_percent").between(0,100)
)

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

vehicle = (
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
          F.col("total_distance_km") /
          F.col("total_battery_consumed")
      )
)

model = (
    vehicle.groupBy("model")
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

region = (
    vehicle.groupBy("region")
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

trend = (
    df.withColumn("date", F.to_date("timestamp"))
    .groupBy("date")
    .agg(
        F.avg("estimated_range_km").alias("avg_estimated_range_km"),
        F.avg("battery_percent").alias("avg_battery_percent")
    )
)

vehicle.write.mode("overwrite").parquet(args["output_path"]+"/vehicle_efficiency/")
model.write.mode("overwrite").parquet(args["output_path"]+"/model_efficiency/")
region.write.mode("overwrite").parquet(args["output_path"]+"/region_efficiency/")
trend.write.mode("overwrite").parquet(args["output_path"]+"/range_trend/")
