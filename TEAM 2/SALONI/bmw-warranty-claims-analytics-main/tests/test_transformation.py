import pytest
from pyspark.sql import SparkSession

from src.processing.validate_warranty import enrich_claims


@pytest.fixture(scope="module")
def spark():
    spark = (
        SparkSession.builder
        .master("local[2]")
        .appName("BMWTransformationTests")
        .getOrCreate()
    )

    yield spark

    spark.stop()


def test_valid_claim_is_enriched_with_vehicle_details(spark):
    warranty_data = [
        (
            "CLM001",
            "BMWV001",
            "2025-01-10",
            "Engine",
            2500.00,
            "Approved",
            "2025-01-10",
            "VALID",
            "",
        )
    ]

    vehicle_data = [
        (
            "BMWV001",
            "WBA123456789",
            "BMW 3 Series",
            2024,
            "Petrol",
            "Europe",
            "2024-01-15",
        )
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
            "claim_date_parsed",
            "validation_status",
            "rejection_reason",
        ],
    )

    vehicle_df = spark.createDataFrame(
        vehicle_data,
        [
            "vehicle_id",
            "vin",
            "model",
            "model_year",
            "fuel_type",
            "region",
            "manufacturing_date",
        ],
    )

    enriched_df = enrich_claims(warranty_df, vehicle_df)

    assert enriched_df.count() == 1

    row = enriched_df.first()

    assert row["claim_id"] == "CLM001"
    assert row["vehicle_id"] == "BMWV001"
    assert row["vin"] == "WBA123456789"
    assert row["model"] == "BMW 3 Series"
    assert row["model_year"] == 2024
    assert row["fuel_type"] == "Petrol"
    assert row["region"] == "Europe"