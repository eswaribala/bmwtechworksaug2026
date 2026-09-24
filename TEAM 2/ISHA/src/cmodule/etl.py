from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# ====================================
# Spark Session
# ====================================

spark = (
    SparkSession.builder
    .appName("BMW_Service_Centre_ETL")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# ====================================
# Read Source Files
# ====================================

data_dir = Path(__file__).resolve().parent / "data"
output_dir = Path(__file__).resolve().parents[2]

dealer_df = spark.read.csv(
    str(data_dir / "dealer_large.csv"),
    header=True,
    inferSchema=True
)

maintenance_df = spark.read.csv(
    str(data_dir / "maintenance_large_100k.csv"),
    header=True,
    inferSchema=True
)

print(f"Dealer Records: {dealer_df.count()}")
print(f"Maintenance Records: {maintenance_df.count()}")

# ====================================
# Data Cleaning
# ====================================

maintenance_clean = maintenance_df.dropna(
    subset=[
        "service_id",
        "vehicle_id",
        "dealer_id"
    ]
)

maintenance_clean = (
    maintenance_clean
    .dropDuplicates(["service_id"])
)

maintenance_clean = (
    maintenance_clean
    .filter(col("parts_cost") >= 0)
    .filter(col("labour_cost") >= 0)
)

# ====================================
# Add Repair Cost
# ====================================

maintenance_clean = (
    maintenance_clean
    .withColumn(
        "repair_cost",
        col("parts_cost") + col("labour_cost")
    )
)

# ====================================
# Join With Dealer
# ====================================

joined_df = (
    maintenance_clean
    .join(
        dealer_df,
        on="dealer_id",
        how="inner"
    )
)

# ====================================
# Export Clean Data
# ====================================

maintenance_clean.toPandas().to_csv(
    output_dir / "maintenance_cleaned.csv",
    index=False
)

joined_df.toPandas().to_csv(
    output_dir / "maintenance_dealer_joined.csv",
    index=False
)

print("\nETL Completed")
print("maintenance_cleaned.csv created")
print("maintenance_dealer_joined.csv created")

spark.stop()