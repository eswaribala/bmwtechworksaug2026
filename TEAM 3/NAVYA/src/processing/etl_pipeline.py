# ============================================================
# BMW Enterprise Batch ETL Pipeline
# ============================================================
# Flow:
# Local CSV
#    ↓
# PySpark
#    ↓
# Schema Validation
#    ↓
# Data Quality Checks
#    ↓
# Remove Invalid Records
#    ↓
# Remove Duplicates
#    ↓
# Business Transformations
#    ↓
# Partitioned Processed Parquet
#    ↓
# Rejected Parquet
# ============================================================

import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round
from pyspark.sql.types import (
    DateType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

from src.utils.logger import logger
from src.validation.data_quality import (
    check_duplicates,
    check_invalid_dates,
    check_invalid_range,
    check_nulls,
    remove_duplicates,
)


# ============================================================
# JAVA 21 CONFIGURATION
# ============================================================
# Supports:
# 1. GitHub Actions / Linux
#    → Uses the JAVA_HOME supplied by the environment.
#
# 2. Local Windows development
#    → Falls back to the installed Temurin Java 21 path.
# ============================================================

JAVA_HOME = os.environ.get("JAVA_HOME")

if JAVA_HOME:
    logger.info(
        "Using JAVA_HOME from environment: %s",
        JAVA_HOME,
    )

else:
    windows_java_home = Path(
        r"C:\Users\NavyaS\AppData\Local\Programs\Eclipse Adoptium"
        r"\jdk-21.0.12.101-hotspot"
    )

    if windows_java_home.exists():

        JAVA_HOME = str(windows_java_home)

        os.environ["JAVA_HOME"] = JAVA_HOME

        os.environ["PATH"] = (
            os.path.join(JAVA_HOME, "bin")
            + os.pathsep
            + os.environ["PATH"]
        )

        logger.info(
            "Using local Windows Java 21: %s",
            JAVA_HOME,
        )

    else:
        logger.info(
            "JAVA_HOME was not set and local Windows Java 21 "
            "was not found. Using system Java configuration."
        )


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REJECTED_DIR = PROJECT_ROOT / "data" / "rejected"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

REJECTED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# INPUT FILES
# ============================================================

VEHICLE_FILE = SAMPLE_DIR / "vehicle_master.csv"
SALES_FILE = SAMPLE_DIR / "sales.csv"
MAINTENANCE_FILE = SAMPLE_DIR / "maintenance.csv"
DEALER_FILE = SAMPLE_DIR / "dealer.csv"


# ============================================================
# SPARK SESSION
# ============================================================

spark = (
    SparkSession.builder
    .appName("BMW-Enterprise-Batch-ETL")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

logger.info("ETL pipeline started")
logger.info("Spark session created successfully")


# ============================================================
# 1. DEFINE SCHEMAS
# ============================================================

vehicle_schema = StructType([
    StructField("vehicle_id", StringType(), True),
    StructField("vin", StringType(), True),
    StructField("model", StringType(), True),
    StructField("model_year", IntegerType(), True),
    StructField("fuel_type", StringType(), True),
    StructField("region", StringType(), True),
    StructField("manufacturing_date", DateType(), True),
])


sales_schema = StructType([
    StructField("sale_id", StringType(), True),
    StructField("vehicle_id", StringType(), True),
    StructField("dealer_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("sale_date", DateType(), True),
    StructField("model", StringType(), True),
    StructField("region", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("quantity", IntegerType(), True),
])


maintenance_schema = StructType([
    StructField("service_id", StringType(), True),
    StructField("vehicle_id", StringType(), True),
    StructField("dealer_id", StringType(), True),
    StructField("service_date", DateType(), True),
    StructField("service_type", StringType(), True),
    StructField("odometer", IntegerType(), True),
    StructField("parts_cost", DoubleType(), True),
    StructField("labour_cost", DoubleType(), True),
    StructField("failure_code", StringType(), True),
])


dealer_schema = StructType([
    StructField("dealer_id", StringType(), True),
    StructField("dealer_name", StringType(), True),
    StructField("city", StringType(), True),
    StructField("region", StringType(), True),
    StructField("capacity", IntegerType(), True),
    StructField("rating", DoubleType(), True),
])


# ============================================================
# 2. READ RAW CSV DATA
# ============================================================

print("\n============================================================")
print("READING RAW BMW DATA")
print("============================================================")

try:

    vehicle_df = (
        spark.read
        .option("header", True)
        .schema(vehicle_schema)
        .csv(str(VEHICLE_FILE))
    )

    sales_df = (
        spark.read
        .option("header", True)
        .schema(sales_schema)
        .csv(str(SALES_FILE))
    )

    maintenance_df = (
        spark.read
        .option("header", True)
        .schema(maintenance_schema)
        .csv(str(MAINTENANCE_FILE))
    )

    dealer_df = (
        spark.read
        .option("header", True)
        .schema(dealer_schema)
        .csv(str(DEALER_FILE))
    )

    logger.info(
        "All raw BMW datasets loaded successfully"
    )

except Exception as exc:

    logger.exception(
        "Failed to load raw BMW datasets"
    )

    spark.stop()

    raise RuntimeError(
        f"ETL ingestion failed: {exc}"
    ) from exc


# ============================================================
# 3. DISPLAY RAW DATA INFORMATION
# ============================================================

print("\nRAW ROW COUNTS")
print("--------------")

vehicle_count = vehicle_df.count()
sales_count = sales_df.count()
maintenance_count = maintenance_df.count()
dealer_count = dealer_df.count()

print("Vehicle Master :", vehicle_count)
print("Sales          :", sales_count)
print("Maintenance    :", maintenance_count)
print("Dealer         :", dealer_count)

logger.info(
    "Raw record counts | Vehicle=%s | Sales=%s | "
    "Maintenance=%s | Dealer=%s",
    vehicle_count,
    sales_count,
    maintenance_count,
    dealer_count,
)


print("\nVEHICLE MASTER SCHEMA")
vehicle_df.printSchema()

print("\nSALES SCHEMA")
sales_df.printSchema()

print("\nMAINTENANCE SCHEMA")
maintenance_df.printSchema()

print("\nDEALER SCHEMA")
dealer_df.printSchema()


# ============================================================
# 4. DATA QUALITY CHECKS
# ============================================================

print("\n============================================================")
print("DATA QUALITY CHECKS")
print("============================================================")

print("\nVehicle Master - Null Counts")
check_nulls(vehicle_df).show(truncate=False)

print("\nSales - Null Counts")
check_nulls(sales_df).show(truncate=False)

print("\nMaintenance - Null Counts")
check_nulls(maintenance_df).show(truncate=False)

print("\nDealer - Null Counts")
check_nulls(dealer_df).show(truncate=False)

logger.info(
    "Null-value checks completed"
)


# ============================================================
# 5. DUPLICATE CHECKS
# ============================================================

print("\n============================================================")
print("DUPLICATE CHECKS")
print("============================================================")

print("\nVehicle Master duplicates")

check_duplicates(
    vehicle_df,
    "vehicle_id",
).show()


print("\nSales duplicates")

check_duplicates(
    sales_df,
    "sale_id",
).show()


print("\nMaintenance duplicates")

check_duplicates(
    maintenance_df,
    "service_id",
).show()


print("\nDealer duplicates")

check_duplicates(
    dealer_df,
    "dealer_id",
).show()

logger.info(
    "Duplicate checks completed"
)


# ============================================================
# 6. INVALID RANGE CHECKS
# ============================================================

print("\n============================================================")
print("INVALID RANGE CHECKS")
print("============================================================")

print("\nVehicle Master - Invalid Model Year")

check_invalid_range(
    vehicle_df,
    "model_year",
    2000,
    2026,
).select(
    "vehicle_id",
    "model_year",
).show()


print("\nSales - Invalid Price")

check_invalid_range(
    sales_df,
    "price",
    0,
    100000000,
).select(
    "sale_id",
    "price",
).show()


print("\nMaintenance - Invalid Parts Cost")

check_invalid_range(
    maintenance_df,
    "parts_cost",
    0,
    100000000,
).select(
    "service_id",
    "parts_cost",
).show()


print("\nDealer - Invalid Rating")

check_invalid_range(
    dealer_df,
    "rating",
    0,
    5,
).select(
    "dealer_id",
    "rating",
).show()

logger.info(
    "Invalid-range checks completed"
)


# ============================================================
# 7. INVALID DATE CHECKS
# ============================================================

print("\n============================================================")
print("INVALID DATE CHECKS")
print("============================================================")

print("\nSales - Invalid Sale Dates")

check_invalid_dates(
    sales_df,
    "sale_date",
).select(
    "sale_id",
    "sale_date",
).show()


print("\nMaintenance - Invalid Service Dates")

check_invalid_dates(
    maintenance_df,
    "service_date",
).select(
    "service_id",
    "service_date",
).show()

logger.info(
    "Invalid-date checks completed"
)


# ============================================================
# 8. CLEAN VEHICLE MASTER
# ============================================================

print("\n============================================================")
print("CLEANING VEHICLE MASTER")
print("============================================================")

vehicle_rejected = vehicle_df.filter(
    col("vehicle_id").isNull()
    | col("model_year").isNull()
    | (col("model_year") < 2000)
    | (col("model_year") > 2026)
)

vehicle_valid = vehicle_df.filter(
    col("vehicle_id").isNotNull()
    & col("model_year").isNotNull()
    & (col("model_year") >= 2000)
    & (col("model_year") <= 2026)
)

vehicle_clean = remove_duplicates(
    vehicle_valid,
    "vehicle_id",
)

vehicle_rejected_count = vehicle_rejected.count()
vehicle_valid_count = vehicle_valid.count()
vehicle_clean_count = vehicle_clean.count()

print("Original records :", vehicle_count)
print("Rejected records :", vehicle_rejected_count)
print("Valid records    :", vehicle_valid_count)
print("Clean records    :", vehicle_clean_count)

logger.info(
    "Vehicle Master cleaning completed | "
    "Original=%s | Rejected=%s | Clean=%s",
    vehicle_count,
    vehicle_rejected_count,
    vehicle_clean_count,
)


# ============================================================
# 9. CLEAN SALES
# ============================================================

print("\n============================================================")
print("CLEANING SALES")
print("============================================================")

sales_rejected = sales_df.filter(
    col("sale_id").isNull()
    | col("vehicle_id").isNull()
    | col("sale_date").isNull()
    | col("price").isNull()
    | (col("price") < 0)
    | col("quantity").isNull()
    | (col("quantity") <= 0)
)

sales_valid = sales_df.filter(
    col("sale_id").isNotNull()
    & col("vehicle_id").isNotNull()
    & col("sale_date").isNotNull()
    & col("price").isNotNull()
    & (col("price") >= 0)
    & col("quantity").isNotNull()
    & (col("quantity") > 0)
)

sales_clean = remove_duplicates(
    sales_valid,
    "sale_id",
)

sales_rejected_count = sales_rejected.count()
sales_valid_count = sales_valid.count()
sales_clean_count = sales_clean.count()

print("Original records :", sales_count)
print("Rejected records :", sales_rejected_count)
print("Valid records    :", sales_valid_count)
print("Clean records    :", sales_clean_count)

logger.info(
    "Sales cleaning completed | "
    "Original=%s | Rejected=%s | Clean=%s",
    sales_count,
    sales_rejected_count,
    sales_clean_count,
)


# ============================================================
# 10. CLEAN MAINTENANCE
# ============================================================

print("\n============================================================")
print("CLEANING MAINTENANCE")
print("============================================================")

maintenance_rejected = maintenance_df.filter(
    col("service_id").isNull()
    | col("vehicle_id").isNull()
    | col("service_date").isNull()
    | col("odometer").isNull()
    | (col("odometer") < 0)
    | col("parts_cost").isNull()
    | (col("parts_cost") < 0)
    | col("labour_cost").isNull()
    | (col("labour_cost") < 0)
)

maintenance_valid = maintenance_df.filter(
    col("service_id").isNotNull()
    & col("vehicle_id").isNotNull()
    & col("service_date").isNotNull()
    & col("odometer").isNotNull()
    & (col("odometer") >= 0)
    & col("parts_cost").isNotNull()
    & (col("parts_cost") >= 0)
    & col("labour_cost").isNotNull()
    & (col("labour_cost") >= 0)
)

maintenance_clean = remove_duplicates(
    maintenance_valid,
    "service_id",
)

maintenance_rejected_count = maintenance_rejected.count()
maintenance_valid_count = maintenance_valid.count()
maintenance_clean_count = maintenance_clean.count()

print("Original records :", maintenance_count)
print("Rejected records :", maintenance_rejected_count)
print("Valid records    :", maintenance_valid_count)
print("Clean records    :", maintenance_clean_count)

logger.info(
    "Maintenance cleaning completed | "
    "Original=%s | Rejected=%s | Clean=%s",
    maintenance_count,
    maintenance_rejected_count,
    maintenance_clean_count,
)


# ============================================================
# 11. CLEAN DEALER
# ============================================================

print("\n============================================================")
print("CLEANING DEALER")
print("============================================================")

dealer_rejected = dealer_df.filter(
    col("dealer_id").isNull()
    | col("dealer_name").isNull()
    | col("city").isNull()
    | col("region").isNull()
    | col("capacity").isNull()
    | (col("capacity") < 0)
    | col("rating").isNull()
    | (col("rating") < 0)
    | (col("rating") > 5)
)

dealer_valid = dealer_df.filter(
    col("dealer_id").isNotNull()
    & col("dealer_name").isNotNull()
    & col("city").isNotNull()
    & col("region").isNotNull()
    & col("capacity").isNotNull()
    & (col("capacity") >= 0)
    & col("rating").isNotNull()
    & (col("rating") <= 5)
)

dealer_clean = remove_duplicates(
    dealer_valid,
    "dealer_id",
)

dealer_rejected_count = dealer_rejected.count()
dealer_valid_count = dealer_valid.count()
dealer_clean_count = dealer_clean.count()

print("Original records :", dealer_count)
print("Rejected records :", dealer_rejected_count)
print("Valid records    :", dealer_valid_count)
print("Clean records    :", dealer_clean_count)

logger.info(
    "Dealer cleaning completed | "
    "Original=%s | Rejected=%s | Clean=%s",
    dealer_count,
    dealer_rejected_count,
    dealer_clean_count,
)


# ============================================================
# 12. BUSINESS TRANSFORMATIONS
# ============================================================

print("\n============================================================")
print("BUSINESS TRANSFORMATIONS")
print("============================================================")

sales_processed = (
    sales_clean
    .withColumn(
        "revenue",
        round(
            col("price") * col("quantity"),
            2,
        ),
    )
)

maintenance_processed = (
    maintenance_clean
    .withColumn(
        "total_service_cost",
        round(
            col("parts_cost") + col("labour_cost"),
            2,
        ),
    )
)

print("\nSales Processed Sample")

sales_processed.show(
    5,
    truncate=False,
)


print("\nMaintenance Processed Sample")

maintenance_processed.show(
    5,
    truncate=False,
)

logger.info(
    "Business transformations completed"
)


# ============================================================
# 13. LOCAL PARQUET OUTPUT HELPER
# ============================================================

def write_parquet_with_pyarrow(
    dataframe,
    output_directory: Path,
    partition_column: str | None = None,
):
    """
    Write a PySpark DataFrame as local Parquet.

    PySpark performs the ETL processing.
    PyArrow is used for local Windows Parquet output.

    When partition_column is provided, the output is written
    as a Hive-style partitioned Parquet dataset.
    """

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:

        pandas_df = dataframe.toPandas()

        # ----------------------------------------------------
        # PARTITIONED PARQUET OUTPUT
        # ----------------------------------------------------

        if partition_column:

            if partition_column not in pandas_df.columns:
                raise ValueError(
                    f"Partition column '{partition_column}' "
                    f"does not exist in the dataframe"
                )

            pandas_df[partition_column] = (
                pandas_df[partition_column]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .replace("", "Unknown")
            )

            pandas_df.to_parquet(
                output_directory,
                engine="pyarrow",
                index=False,
                partition_cols=[partition_column],
            )

            print(
                f"Partitioned Parquet written to: "
                f"{output_directory}"
            )

            logger.info(
                "Partitioned Parquet written successfully | "
                "Path=%s | Partition=%s",
                output_directory,
                partition_column,
            )

        # ----------------------------------------------------
        # NORMAL PARQUET OUTPUT
        # ----------------------------------------------------

        else:

            arrow_table = pa.Table.from_pandas(
                pandas_df,
                preserve_index=False,
            )

            output_file = (
                output_directory
                / "part-00000.parquet"
            )

            pq.write_table(
                arrow_table,
                str(output_file),
            )

            print(
                f"Parquet written to: {output_file}"
            )

            logger.info(
                "Parquet file written successfully: %s",
                output_file,
            )

    except Exception as exc:

        logger.exception(
            "Failed to write Parquet output: %s",
            output_directory,
        )

        raise RuntimeError(
            f"Parquet output failed for "
            f"{output_directory}: {exc}"
        ) from exc


# ============================================================
# 14. WRITE PROCESSED PARQUET FILES
# ============================================================

print("\n============================================================")
print("WRITING PROCESSED PARQUET FILES")
print("============================================================")

write_parquet_with_pyarrow(
    vehicle_clean,
    PROCESSED_DIR / "vehicle_master",
)

# Sales is partitioned by region.
write_parquet_with_pyarrow(
    sales_processed,
    PROCESSED_DIR / "sales",
    partition_column="region",
)

write_parquet_with_pyarrow(
    maintenance_processed,
    PROCESSED_DIR / "maintenance",
)

write_parquet_with_pyarrow(
    dealer_clean,
    PROCESSED_DIR / "dealer",
)


# ============================================================
# 15. WRITE REJECTED PARQUET FILES
# ============================================================

print("\n============================================================")
print("WRITING REJECTED PARQUET FILES")
print("============================================================")

write_parquet_with_pyarrow(
    vehicle_rejected,
    REJECTED_DIR / "vehicle_master",
)

write_parquet_with_pyarrow(
    sales_rejected,
    REJECTED_DIR / "sales",
)

write_parquet_with_pyarrow(
    maintenance_rejected,
    REJECTED_DIR / "maintenance",
)

write_parquet_with_pyarrow(
    dealer_rejected,
    REJECTED_DIR / "dealer",
)


# ============================================================
# 16. FINAL SUMMARY
# ============================================================

logger.info(
    "ETL processing completed successfully"
)

print("\n============================================================")
print("ETL PIPELINE COMPLETED SUCCESSFULLY")
print("============================================================")

print("\nProcessed output directory:")
print(PROCESSED_DIR)

print("\nRejected output directory:")
print(REJECTED_DIR)

print("\nGenerated processed datasets:")
print("  - vehicle_master")
print("  - sales (partitioned by region)")
print("  - maintenance")
print("  - dealer")

print("\nGenerated rejected datasets:")
print("  - vehicle_master")
print("  - sales")
print("  - maintenance")
print("  - dealer")

print("\nETL flow completed:")
print("  CSV")
print("   ↓")
print("  PySpark")
print("   ↓")
print("  Schema Validation")
print("   ↓")
print("  Data Quality Validation")
print("   ↓")
print("  Invalid Records → Rejected Parquet")
print("   ↓")
print("  Cleaning & Deduplication")
print("   ↓")
print("  Business Transformations")
print("   ↓")
print("  Region-Partitioned Processed Parquet")

print("\n============================================================")


# ============================================================
# STOP SPARK
# ============================================================

spark.stop()

logger.info(
    "Spark session stopped"
)

logger.info(
    "BMW Enterprise Batch ETL pipeline finished"
)