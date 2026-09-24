import logging
import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    trim,
    try_to_date,
    when,
    lit,
    concat_ws,
)


# ============================================================
# CONFIGURATION
# ============================================================

BUCKET_NAME = "bmw-warranty-claims-532404260630"

WARRANTY_PATH = (
    f"s3a://{BUCKET_NAME}/raw/warranty/warranty_claims.csv"
)

VEHICLE_MASTER_PATH = (
    f"s3a://{BUCKET_NAME}/raw/vehicle_master/vehicle_master.csv"
)

PROCESSED_VALID_PATH = (
    f"s3a://{BUCKET_NAME}/processed/warranty_valid"
)

PROCESSED_REJECTED_PATH = (
    f"s3a://{BUCKET_NAME}/processed/warranty_rejected"
)

PROCESSED_ENRICHED_PATH = (
    f"s3a://{BUCKET_NAME}/processed/warranty_enriched"
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# SPARK SESSION
# ============================================================

def create_spark_session():
    logger.info("Creating Spark session")

    spark = (
        SparkSession.builder
        .appName("BMWWarrantyValidation")
        .master("local[*]")
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.5.0",
        )
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider",
        )
        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem",
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    logger.info(
        "Spark session created successfully. Version: %s",
        spark.version,
    )

    return spark


# ============================================================
# READ DATA
# ============================================================

def read_input_data(spark):
    logger.info("Reading Warranty Claims from S3")
    logger.info("Path: %s", WARRANTY_PATH)

    warranty_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(WARRANTY_PATH)
    )

    logger.info(
        "Warranty Claims loaded. Row count: %s",
        warranty_df.count(),
    )

    logger.info("Reading Vehicle Master from S3")
    logger.info("Path: %s", VEHICLE_MASTER_PATH)

    vehicle_df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(VEHICLE_MASTER_PATH)
    )

    logger.info(
        "Vehicle Master loaded. Row count: %s",
        vehicle_df.count(),
    )

    return warranty_df, vehicle_df


# ============================================================
# VALIDATE WARRANTY CLAIMS
# ============================================================

def validate_warranty_claims(warranty_df, vehicle_df):

    logger.info("Starting warranty claim validation")

    # --------------------------------------------------------
    # Clean string columns
    # --------------------------------------------------------

    df = (
        warranty_df
        .withColumn("claim_id", trim(col("claim_id")))
        .withColumn("vehicle_id", trim(col("vehicle_id")))
        .withColumn("component", trim(col("component")))
        .withColumn("claim_status", trim(col("claim_status")))
    )

    # --------------------------------------------------------
    # Convert claim_date into proper date
    # --------------------------------------------------------

    df = df.withColumn(
        "claim_date_parsed",
        try_to_date(col("claim_date"), "yyyy-MM-dd"),
    )

    # --------------------------------------------------------
    # Validate vehicle_id against Vehicle Master
    # --------------------------------------------------------

    valid_vehicle_ids = (
        vehicle_df
        .select("vehicle_id")
        .where(col("vehicle_id").isNotNull())
        .dropDuplicates()
    )

    df = df.join(
        valid_vehicle_ids.withColumn("vehicle_exists", lit(True)),
        on="vehicle_id",
        how="left",
    )

    # --------------------------------------------------------
    # Create rejection reasons
    # --------------------------------------------------------

    df = df.withColumn(
        "rejection_reason",
        concat_ws(
            "; ",
            when(
                col("claim_id").isNull() |
                (col("claim_id") == ""),
                lit("Missing claim_id"),
            ),
            when(
                col("vehicle_id").isNull() |
                (col("vehicle_id") == ""),
                lit("Missing vehicle_id"),
            ),
            when(
                col("vehicle_exists").isNull(),
                lit("Vehicle not found in vehicle_master"),
            ),
            when(
                col("claim_date_parsed").isNull(),
                lit("Invalid claim_date"),
            ),
            when(
                col("component").isNull() |
                (col("component") == ""),
                lit("Missing component"),
            ),
            when(
                col("claim_amount").isNull(),
                lit("Missing claim_amount"),
            ),
            when(
                col("claim_amount") < 0,
                lit("Negative claim_amount"),
            ),
            when(
                col("claim_status").isNull() |
                (col("claim_status") == ""),
                lit("Missing claim_status"),
            ),
        ),
    )

    # --------------------------------------------------------
    # Determine valid/rejected records
    # --------------------------------------------------------

    df = df.withColumn(
        "validation_status",
        when(
            col("rejection_reason") == "",
            lit("VALID"),
        ).otherwise(
            lit("REJECTED"),
        ),
    )

    # --------------------------------------------------------
    # Valid records
    # --------------------------------------------------------

    valid_df = (
        df
        .filter(col("validation_status") == "VALID")
        .drop("vehicle_exists")
    )

    # --------------------------------------------------------
    # Rejected records
    # --------------------------------------------------------

    rejected_df = (
        df
        .filter(col("validation_status") == "REJECTED")
        .drop("vehicle_exists")
    )

    return valid_df, rejected_df


# ============================================================
# ENRICH VALID CLAIMS
# ============================================================

def enrich_claims(valid_df, vehicle_df):
    """
    Enrich valid warranty claims with vehicle master information.
    """

    logger.info("Joining valid warranty claims with Vehicle Master")

    # Select only the required warranty columns first.
    # This removes any duplicate columns that may have been created
    # during the validation transformations.
    claims = valid_df.select(
        "claim_id",
        "vehicle_id",
        "claim_date",
        "component",
        "claim_amount",
        "claim_status",
        "claim_date_parsed",
        "validation_status",
        "rejection_reason",
    ).alias("claims")

    # Select only vehicle-master columns needed for enrichment.
    vehicles = vehicle_df.select(
        "vehicle_id",
        "vin",
        "model",
        "model_year",
        "fuel_type",
        "region",
        "manufacturing_date",
    ).alias("vehicles")

    enriched_df = (
        claims
        .join(
            vehicles,
            col("claims.vehicle_id") == col("vehicles.vehicle_id"),
            "left",
        )
        .select(
            col("claims.claim_id").alias("claim_id"),
            col("claims.vehicle_id").alias("vehicle_id"),
            col("claims.claim_date").alias("claim_date"),
            col("claims.component").alias("component"),
            col("claims.claim_amount").alias("claim_amount"),
            col("claims.claim_status").alias("claim_status"),
            col("claims.claim_date_parsed").alias("claim_date_parsed"),
            col("claims.validation_status").alias("validation_status"),
            col("claims.rejection_reason").alias("rejection_reason"),
            col("vehicles.vin").alias("vin"),
            col("vehicles.model").alias("model"),
            col("vehicles.model_year").alias("model_year"),
            col("vehicles.fuel_type").alias("fuel_type"),
            col("vehicles.region").alias("region"),
            col("vehicles.manufacturing_date").alias("manufacturing_date"),
        )
    )

    return enriched_df


# ============================================================
# WRITE OUTPUTS
# ============================================================

def write_outputs(valid_df, rejected_df, enriched_df):

    logger.info("Writing processed datasets to S3")

    logger.info(
        "Writing valid claims to: %s",
        PROCESSED_VALID_PATH,
    )

    (
        valid_df
        .write
        .mode("overwrite")
        .parquet(PROCESSED_VALID_PATH)
    )

    logger.info(
        "Writing rejected claims to: %s",
        PROCESSED_REJECTED_PATH,
    )

    (
        rejected_df
        .write
        .mode("overwrite")
        .parquet(PROCESSED_REJECTED_PATH)
    )

    logger.info(
        "Writing enriched claims to: %s",
        PROCESSED_ENRICHED_PATH,
    )

    (
        enriched_df
        .write
        .mode("overwrite")
        .parquet(PROCESSED_ENRICHED_PATH)
    )

    logger.info("All processed datasets written successfully")


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("=" * 60)
    logger.info("Starting BMW Warranty Claims Validation Pipeline")
    logger.info("=" * 60)

    # Check credentials without printing secrets
    logger.info(
        "AWS_ACCESS_KEY_ID configured: %s",
        bool(os.environ.get("AWS_ACCESS_KEY_ID")),
    )

    logger.info(
        "AWS_SECRET_ACCESS_KEY configured: %s",
        bool(os.environ.get("AWS_SECRET_ACCESS_KEY")),
    )

    spark = None

    try:

        # ----------------------------------------------------
        # Create Spark
        # ----------------------------------------------------

        spark = create_spark_session()

        # ----------------------------------------------------
        # Read raw data
        # ----------------------------------------------------

        warranty_df, vehicle_df = read_input_data(spark)

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        valid_df, rejected_df = validate_warranty_claims(
            warranty_df,
            vehicle_df,
        )

        # ----------------------------------------------------
        # Counts
        # ----------------------------------------------------

        raw_count = warranty_df.count()
        valid_count = valid_df.count()
        rejected_count = rejected_df.count()

        logger.info("=" * 60)
        logger.info("DATA QUALITY SUMMARY")
        logger.info("=" * 60)

        logger.info("Raw warranty records: %s", raw_count)
        logger.info("Valid warranty records: %s", valid_count)
        logger.info("Rejected warranty records: %s", rejected_count)

        # ----------------------------------------------------
        # Show rejection reasons
        # ----------------------------------------------------

        logger.info("Rejected record reasons:")

        (
            rejected_df
            .groupBy("rejection_reason")
            .count()
            .orderBy(col("count").desc())
            .show(truncate=False)
        )

        # ----------------------------------------------------
        # Enrich valid records
        # ----------------------------------------------------

        enriched_df = enrich_claims(
            valid_df,
            vehicle_df,
        )

        enriched_count = enriched_df.count()

        logger.info(
            "Enriched warranty records: %s",
            enriched_count,
        )

        # ----------------------------------------------------
        # Display samples
        # ----------------------------------------------------

        logger.info("Sample valid records:")

        valid_df.show(
            5,
            truncate=False,
        )

        logger.info("Sample rejected records:")

        rejected_df.show(
            5,
            truncate=False,
        )

        logger.info("Sample enriched records:")

        enriched_df.show(
            5,
            truncate=False,
        )

        # ----------------------------------------------------
        # Write Parquet
        # ----------------------------------------------------

        write_outputs(
            valid_df,
            rejected_df,
            enriched_df,
        )

        logger.info("=" * 60)
        logger.info("BMW Warranty Claims Pipeline Completed Successfully")
        logger.info("=" * 60)

    except Exception as exc:

        logger.exception(
            "BMW Warranty Claims Pipeline Failed: %s",
            exc,
        )

        raise

    finally:

        if spark is not None:

            logger.info("Stopping Spark session")

            spark.stop()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()