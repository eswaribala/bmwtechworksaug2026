import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

from src.processing.validate_warranty import validate_warranty_claims


@pytest.fixture(scope="module")
def spark():
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("BMWWarrantyTests")
        .getOrCreate()
    )

    yield spark

    spark.stop()


def test_valid_claim_is_accepted(spark):
    warranty_data = [
        ("CLM001", "BMWV001", "2025-01-10", "Engine", 2500.00, "Approved")
    ]

    vehicle_data = [
        ("BMWV001",)
    ]

    warranty_schema = StructType([
        StructField("claim_id", StringType(), True),
        StructField("vehicle_id", StringType(), True),
        StructField("claim_date", StringType(), True),
        StructField("component", StringType(), True),
        StructField("claim_amount", DoubleType(), True),
        StructField("claim_status", StringType(), True),
    ])

    warranty_df = spark.createDataFrame(
        warranty_data,
        warranty_schema,
    )
    
    vehicle_df = spark.createDataFrame(
        vehicle_data,
        ["vehicle_id"],
    )

    valid_df, rejected_df = validate_warranty_claims(
        warranty_df,
        vehicle_df,
    )

    assert valid_df.count() == 1
    assert rejected_df.count() == 0


def test_missing_claim_id_is_rejected(spark):
    warranty_data = [
        (None, "BMWV001", "2025-01-10", "Engine", 2500.00, "Approved")
    ]

    vehicle_data = [
        ("BMWV001",)
    ]

    warranty_schema = StructType([
        StructField("claim_id", StringType(), True),
        StructField("vehicle_id", StringType(), True),
        StructField("claim_date", StringType(), True),
        StructField("component", StringType(), True),
        StructField("claim_amount", DoubleType(), True),
        StructField("claim_status", StringType(), True),
    ])

    warranty_df = spark.createDataFrame(
        warranty_data,
        warranty_schema,
    )

    vehicle_df = spark.createDataFrame(
        vehicle_data,
        ["vehicle_id"],
    )

    valid_df, rejected_df = validate_warranty_claims(
        warranty_df,
        vehicle_df,
    )

    assert valid_df.count() == 0
    assert rejected_df.count() == 1

    reason = rejected_df.select("rejection_reason").first()[0]

    assert "Missing claim_id" in reason

def test_unknown_vehicle_is_rejected(spark):
    warranty_data = [
        ("CLM002", "BMWV999", "2025-01-10", "Engine", 2500.00, "Approved")
    ]

    vehicle_data = [
        ("BMWV001",)
    ]

    warranty_df = spark.createDataFrame(
        warranty_data,
        [
            "claim_id",
            "vehicle_id",
            "claim_date",
            "component",
            "claim_amount",
            "claim_status",
        ],
    )

    vehicle_df = spark.createDataFrame(
        vehicle_data,
        ["vehicle_id"],
    )

    valid_df, rejected_df = validate_warranty_claims(
        warranty_df,
        vehicle_df,
    )

    assert valid_df.count() == 0
    assert rejected_df.count() == 1

    reason = rejected_df.select("rejection_reason").first()[0]
    assert "Vehicle not found in vehicle_master" in reason


def test_negative_claim_amount_is_rejected(spark):
    warranty_data = [
        ("CLM003", "BMWV001", "2025-01-10", "Engine", -500.00, "Approved")
    ]

    vehicle_data = [
        ("BMWV001",)
    ]

    warranty_df = spark.createDataFrame(
        warranty_data,
        [
            "claim_id",
            "vehicle_id",
            "claim_date",
            "component",
            "claim_amount",
            "claim_status",
        ],
    )

    vehicle_df = spark.createDataFrame(
        vehicle_data,
        ["vehicle_id"],
    )

    valid_df, rejected_df = validate_warranty_claims(
        warranty_df,
        vehicle_df,
    )

    assert valid_df.count() == 0
    assert rejected_df.count() == 1

    reason = rejected_df.select("rejection_reason").first()[0]
    assert "Negative claim_amount" in reason


def test_invalid_claim_date_is_rejected(spark):
    warranty_data = [
        ("CLM004", "BMWV001", "invalid-date", "Engine", 2500.00, "Approved")
    ]

    vehicle_data = [
        ("BMWV001",)
    ]

    warranty_df = spark.createDataFrame(
        warranty_data,
        [
            "claim_id",
            "vehicle_id",
            "claim_date",
            "component",
            "claim_amount",
            "claim_status",
        ],
    )

    vehicle_df = spark.createDataFrame(
        vehicle_data,
        ["vehicle_id"],
    )

    valid_df, rejected_df = validate_warranty_claims(
        warranty_df,
        vehicle_df,
    )

    assert valid_df.count() == 0
    assert rejected_df.count() == 1

    reason = rejected_df.select("rejection_reason").first()[0]
    assert "Invalid claim_date" in reason