from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "src" / "pysparkmodule" / "data"
MONTHLY_DATASET_PATH = DATA_DIR / "bmw_monthly_sales_dataset.csv"
FORECAST_OUTPUT_PATH = DATA_DIR / "bmw_next_month_forecast.csv"


def test_monthly_dataset_exists():
    assert MONTHLY_DATASET_PATH.exists(), f"Missing monthly dataset: {MONTHLY_DATASET_PATH}"


def test_forecast_output_exists():
    assert FORECAST_OUTPUT_PATH.exists(), f"Missing forecast output: {FORECAST_OUTPUT_PATH}"


def test_monthly_dataset_has_required_columns():
    monthly_df = pd.read_csv(MONTHLY_DATASET_PATH)

    expected_columns = {"model", "region", "sale_month", "monthly_revenue", "monthly_units"}
    assert expected_columns.issubset(set(monthly_df.columns)), monthly_df.columns.tolist()
    assert not monthly_df.empty, "Monthly aggregation dataset is empty"


def test_forecast_output_has_required_columns():
    forecast_df = pd.read_csv(FORECAST_OUTPUT_PATH)

    expected_columns = {"forecast_month", "model", "region", "predicted_revenue", "created_at"}
    assert expected_columns.issubset(set(forecast_df.columns)), forecast_df.columns.tolist()
    assert not forecast_df.empty, "Forecast dataset is empty"
    assert (forecast_df["predicted_revenue"].notna()).all(), "Forecast revenue contains nulls"
