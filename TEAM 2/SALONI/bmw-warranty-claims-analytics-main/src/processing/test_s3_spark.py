import logging

from pyspark.sql import SparkSession


# ============================================================
# Configuration
# ============================================================

BUCKET_NAME = "bmw-warranty-claims-532404260630"

WARRANTY_PATH = (
    f"s3a://{BUCKET_NAME}/raw/warranty/warranty_claims.csv"
)

VEHICLE_MASTER_PATH = (
    f"s3a://{BUCKET_NAME}/raw/vehicle_master/vehicle_master.csv"
)


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# Spark Session
# ============================================================

def create_spark_session():
    logger.info("Creating Spark session")

    spark = (
        SparkSession.builder
        .appName("BMWWarrantyS3Test")
        .master("local[*]")

        # Hadoop AWS connector
        .config(
            "spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.5.0",
        )

        # Explicitly tell S3A to use AWS environment variables
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "software.amazon.awssdk.auth.credentials.EnvironmentVariableCredentialsProvider",
        )

        # S3A configuration
        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem",
        )

        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    logger.info("Spark session created successfully")
    logger.info("Spark version: %s", spark.version)

    return spark


# ============================================================
# Read CSV from S3
# ============================================================

def read_csv_from_s3(spark, path, dataset_name):
    logger.info("Reading %s from S3", dataset_name)
    logger.info("S3 path: %s", path)

    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(path)
    )

    logger.info(
        "%s loaded successfully. Row count: %s",
        dataset_name,
        df.count(),
    )

    logger.info("%s schema:", dataset_name)
    df.printSchema()

    logger.info("First 5 rows of %s:", dataset_name)
    df.show(5, truncate=False)

    return df


# ============================================================
# Main
# ============================================================

def main():

    logger.info("=" * 60)
    logger.info("Starting BMW Warranty Claims S3 Spark Test")
    logger.info("=" * 60)

    # Check environment credentials without displaying secrets
    import os

    access_key_exists = bool(os.environ.get("AWS_ACCESS_KEY_ID"))
    secret_key_exists = bool(os.environ.get("AWS_SECRET_ACCESS_KEY"))
    session_token_exists = bool(os.environ.get("AWS_SESSION_TOKEN"))

    logger.info(
        "AWS_ACCESS_KEY_ID configured: %s",
        access_key_exists,
    )

    logger.info(
        "AWS_SECRET_ACCESS_KEY configured: %s",
        secret_key_exists,
    )

    logger.info(
        "AWS_SESSION_TOKEN configured: %s",
        session_token_exists,
    )

    if not access_key_exists or not secret_key_exists:
        raise RuntimeError(
            "AWS credentials are not available in the current PowerShell session. "
            "Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY before running this script."
        )

    spark = None

    try:
        spark = create_spark_session()

        # ----------------------------------------------------
        # Read warranty claims
        # ----------------------------------------------------

        warranty_df = read_csv_from_s3(
            spark,
            WARRANTY_PATH,
            "Warranty Claims",
        )

        # ----------------------------------------------------
        # Read vehicle master
        # ----------------------------------------------------

        vehicle_df = read_csv_from_s3(
            spark,
            VEHICLE_MASTER_PATH,
            "Vehicle Master",
        )

        # ----------------------------------------------------
        # Final success message
        # ----------------------------------------------------

        logger.info("=" * 60)
        logger.info("S3 Spark connectivity test completed successfully")
        logger.info(
            "Warranty Claims rows: %s",
            warranty_df.count(),
        )
        logger.info(
            "Vehicle Master rows: %s",
            vehicle_df.count(),
        )
        logger.info("=" * 60)

    except Exception as exc:
        logger.exception(
            "S3 Spark connectivity test failed: %s",
            exc,
        )
        raise

    finally:
        if spark is not None:
            logger.info("Stopping Spark session")
            spark.stop()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()
