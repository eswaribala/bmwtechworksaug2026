from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    avg,
    max,
    when,
    round
)

# --------------------------------
# Create Spark Session
# --------------------------------

spark = (
    SparkSession.builder
    .appName("BMW Predictive Maintenance")
    .getOrCreate()
)

# --------------------------------
# Load Processed Data
# --------------------------------

telemetry_df = spark.read.csv(
    "data/processed/telemetry.csv",
    header=True,
    inferSchema=True
)

maintenance_df = spark.read.csv(
    "data/processed/maintenance.csv",
    header=True,
    inferSchema=True
)

vehicle_df = spark.read.csv(
    "data/processed/vehicle_master.csv",
    header=True,
    inferSchema=True
)

print(" Data Loaded Successfully")

# --------------------------------
# Fault Count Per Vehicle
# --------------------------------

fault_df = (
    telemetry_df
    .filter(col("fault_code").isNotNull())
    .groupBy("vehicle_id")
    .agg(
        count("fault_code")
        .alias("fault_count")
    )
)

# --------------------------------
# Average Temperature
# --------------------------------

temp_df = (
    telemetry_df
    .groupBy("vehicle_id")
    .agg(
        round(
            avg("temperature"),
            2
        ).alias("avg_temperature")
    )
)

# --------------------------------
# Latest Odometer Reading
# --------------------------------

odometer_df = (
    telemetry_df
    .groupBy("vehicle_id")
    .agg(
        max("odometer")
        .alias("latest_odometer")
    )
)

# --------------------------------
# Maintenance Count
# --------------------------------

maintenance_count_df = (
    maintenance_df
    .groupBy("vehicle_id")
    .agg(
        count("service_id")
        .alias("maintenance_count")
    )
)

# --------------------------------
# Join Everything
# --------------------------------

risk_df = (
    vehicle_df
    .join(fault_df, "vehicle_id", "left")
    .join(temp_df, "vehicle_id", "left")
    .join(odometer_df, "vehicle_id", "left")
    .join(maintenance_count_df, "vehicle_id", "left")
)

# --------------------------------
# Handle Null Values
# --------------------------------

risk_df = risk_df.fillna(0)

# --------------------------------
# Risk Score Calculation
# --------------------------------

risk_df = risk_df.withColumn(
    "risk_score",
    round(
        (
            (col("fault_count") * 1.5)
            + (col("avg_temperature") * 0.20)
            + (col("latest_odometer") / 25000)
            + (col("maintenance_count") * 2)
        ),
        2
    )
)

# --------------------------------
# Risk Category
# --------------------------------

risk_df = risk_df.withColumn(
    "risk_category",
    when(
        col("risk_score") < 50,
        "LOW"
    )
    .when(
        col("risk_score") < 75,
        "MEDIUM"
    )
    .otherwise(
        "HIGH"
    )
)

# --------------------------------
# Primary Risk Factor
# --------------------------------

risk_df = risk_df.withColumn(
    "primary_risk_factor",
    when(
        col("fault_count") > 25,
        "Frequent Faults"
    )
    .when(
        col("maintenance_count") > 8,
        "Frequent Maintenance"
    )
    .when(
        col("latest_odometer") > 220000,
        "High Mileage"
    )
    .otherwise(
        "Temperature Trend"
    )
)

# --------------------------------
# Top 10 Risk Vehicles
# --------------------------------

top10_df = (
    risk_df
    .orderBy(
        col("risk_score").desc()
    )
    .limit(10)
)

# --------------------------------
# Print Results
# --------------------------------

print("\n Top 10 High Risk Vehicles")

top10_df.select(
    "vehicle_id",
    "model",
    "region",
    "fault_count",
    "maintenance_count",
    "latest_odometer",
    "risk_score",
    "risk_category",
    "primary_risk_factor"
).show(
    truncate=False
)

# --------------------------------
# Save Curated Layer
# --------------------------------

risk_df.toPandas().to_csv(
    "data/curated/maintenance_risk_score.csv",
    index=False
)

top10_df.toPandas().to_csv(
    "data/curated/top10_risk_vehicles.csv",
    index=False
)

print("\n Curated Files Generated")

print(
    "\nSaved Files:"
)

print(
    "data/curated/maintenance_risk_score.csv"
)

print(
    "data/curated/top10_risk_vehicles.csv"
)

# --------------------------------
# Stop Spark
# --------------------------------

spark.stop()

print("\n Job Completed Successfully")