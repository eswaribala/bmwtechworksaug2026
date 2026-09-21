from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def test_processed_vehicle_master_exists():
    file_path = (
        PROCESSED_DIR
        / "vehicle_master"
        / "part-00000.parquet"
    )

    assert file_path.exists()

    df = pd.read_parquet(file_path)

    assert not df.empty
    assert "vehicle_id" in df.columns
    assert "model" in df.columns


def test_vehicle_ids_are_unique():
    file_path = (
        PROCESSED_DIR
        / "vehicle_master"
        / "part-00000.parquet"
    )

    df = pd.read_parquet(file_path)

    assert df["vehicle_id"].is_unique


def test_sales_revenue_calculation():
    sales_path = PROCESSED_DIR / "sales"

    df = pd.read_parquet(sales_path)

    expected_revenue = (
        df["price"] * df["quantity"]
    ).round(2)

    assert (
        df["revenue"].round(2)
        == expected_revenue
    ).all()


def test_sales_quantity_is_positive():
    sales_path = PROCESSED_DIR / "sales"

    df = pd.read_parquet(sales_path)

    assert (df["quantity"] > 0).all()


def test_maintenance_total_cost_calculation():
    file_path = (
        PROCESSED_DIR
        / "maintenance"
        / "part-00000.parquet"
    )

    df = pd.read_parquet(file_path)

    expected_total = (
        df["parts_cost"] + df["labour_cost"]
    ).round(2)

    assert (
        df["total_service_cost"].round(2)
        == expected_total
    ).all()