from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "src" / "pysparkmodule" / "data"
PARQUET_PATH = DATA_DIR / "bmw_sales_cleaned.parquet"


def test_cleaned_parquet_exists():
    assert PARQUET_PATH.exists(), f"Missing cleaned parquet dataset: {PARQUET_PATH}"


def test_cleaned_parquet_has_expected_schema():
    df = pd.read_parquet(PARQUET_PATH)

    expected_columns = {
        "sale_id",
        "vehicle_id",
        "dealer_id",
        "customer_id",
        "sale_date",
        "sale_year",
        "sale_month",
        "model",
        "region",
        "price",
        "quantity",
        "revenue",
    }

    assert expected_columns.issubset(set(df.columns)), f"Unexpected columns: {df.columns.tolist()}"
    assert not df.empty, "Cleaned dataset is empty"
    assert (df["price"] > 0).all(), "Price values should be positive"
    assert (df["quantity"] > 0).all(), "Quantity values should be positive"
    assert (df["revenue"] > 0).all(), "Revenue values should be positive"
