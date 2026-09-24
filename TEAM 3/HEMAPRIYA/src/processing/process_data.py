from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, sum


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "dealer_inventory_features.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


# Start Spark
spark = (
    SparkSession.builder
    .appName("BMWDealerInventoryProcessing")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


print("Reading data...")


# Read CSV
df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(str(INPUT_FILE))
)


print("Original row count:", df.count())

print("Original columns:")
df.printSchema()


# --------------------------------------------------
# Data quality checks
# --------------------------------------------------

print("\nMissing values:")

for column in df.columns:
    missing = df.filter(
        col(column).isNull()
    ).count()

    print(f"{column}: {missing}")


# Remove duplicate records
df_clean = df.dropDuplicates()

print(
    "\nRows after removing duplicates:",
    df_clean.count()
)


# Remove rows where important fields are missing
required_columns = [
    "dealer_id",
    "model",
    "region",
    "month",
    "sales",
    "current_inventory",
]

df_clean = df_clean.dropna(
    subset=required_columns
)

print(
    "Rows after removing missing required values:",
    df_clean.count()
)


# --------------------------------------------------
# Business aggregation
# --------------------------------------------------

dealer_model_summary = (
    df_clean
    .groupBy("dealer_id", "model", "region")
    .agg(
        sum("sales").alias("total_sales"),
        avg("sales").alias("average_sales"),
        avg("current_inventory").alias(
            "average_inventory"
        ),
        count("*").alias("number_of_months"),
    )
)


print("\nDealer-model summary:")

dealer_model_summary.show(10)


# --------------------------------------------------
# Save processed data
# --------------------------------------------------

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_path = str(OUTPUT_DIR)

(
    dealer_model_summary
    .coalesce(1)
    .write
    .mode("overwrite")
    .option("header", True)
    .csv(output_path)
)


print(
    "\nProcessed data saved to:",
    output_path
)


spark.stop()

print("Spark processing completed successfully.")