# bmw_sales_forecast.py
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


def main() -> None:
    """Build the monthly sales dataset and forecast the next month's revenue."""
    # ---------------------------------------------------------
    # 1. Paths
    # ---------------------------------------------------------

    # __file__ = .../pysparkws/src/pysparkmodule/forecasting/bmw_sales_forecasting.py
    # parents[3] => .../pysparkws
    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    DATA_DIR = PROJECT_ROOT / "src" / "pysparkmodule" / "data"
    INPUT_PARQUET = DATA_DIR / "bmw_sales_cleaned.parquet"

    if not INPUT_PARQUET.exists():
        raise FileNotFoundError(
            f"Cleaned parquet file not found at: {INPUT_PARQUET}. "
            "Check that the PySpark ETL has run and created the file in "
            "pysparkws/src/pysparkmodule/data/."
        )

    MONTHLY_DATASET_PATH = DATA_DIR / "bmw_monthly_sales_dataset.csv"
    FORECAST_OUTPUT_PATH = DATA_DIR / "bmw_next_month_forecast.csv"

    # ---------------------------------------------------------
    # 2. Load cleaned data
    # ---------------------------------------------------------

    df = pd.read_parquet(INPUT_PARQUET)

    # Keep original pipeline untouched:
    # we read only, we do not overwrite or modify the source Parquet
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df["sale_month"] = df["sale_date"].dt.to_period("M").dt.to_timestamp()

    # ---------------------------------------------------------
    # 3. Build monthly aggregate dataset
    # ---------------------------------------------------------

    monthly_df = (
        df.groupby(["model", "region", "sale_month"], as_index=False)
          .agg(
              monthly_revenue=("revenue", "sum"),
              monthly_units=("quantity", "sum")
          )
          .sort_values(["model", "region", "sale_month"])
          .reset_index(drop=True)
    )

    monthly_df.to_csv(MONTHLY_DATASET_PATH, index=False)
    print(f"Monthly dataset saved to: {MONTHLY_DATASET_PATH}")

    # ---------------------------------------------------------
    # 4. Feature engineering
    # ---------------------------------------------------------

    def add_lag_features(group: pd.DataFrame) -> pd.DataFrame:
        group = group.sort_values("sale_month").copy()
        group["monthly_revenue_lag_1"] = group["monthly_revenue"].shift(1)
        group["monthly_revenue_lag_2"] = group["monthly_revenue"].shift(2)
        group["monthly_revenue_lag_3"] = group["monthly_revenue"].shift(3)
        group["monthly_revenue_lag_6"] = group["monthly_revenue"].shift(6)
        group["monthly_revenue_lag_12"] = group["monthly_revenue"].shift(12)

        for w in [3, 6, 12]:
            group[f"rolling_mean_{w}"] = (
                group["monthly_revenue"]
                .shift(1)
                .rolling(window=w, min_periods=1)
                .mean()
            )

        group["month"] = group["sale_month"].dt.month
        group["year"] = group["sale_month"].dt.year
        group["month_sin"] = np.sin(2 * np.pi * group["month"] / 12)
        group["month_cos"] = np.cos(2 * np.pi * group["month"] / 12)

        group["trend"] = np.arange(len(group))

        return group

    feature_frames = []
    for _, group in monthly_df.groupby(["model", "region"], group_keys=False):
        encoded_group = add_lag_features(group.copy())
        encoded_group["region_code"] = encoded_group["region"].astype("category").cat.codes
        encoded_group["model_code"] = encoded_group["model"].astype("category").cat.codes
        feature_frames.append(encoded_group)

    feature_df = pd.concat(feature_frames, ignore_index=True)

    feature_df = feature_df.dropna(subset=[
        "monthly_revenue_lag_1",
        "monthly_revenue_lag_2",
        "monthly_revenue_lag_3",
        "monthly_revenue_lag_6",
        "monthly_revenue_lag_12"
    ]).copy()

    # ---------------------------------------------------------
    # 5. Train/validation split
    # ---------------------------------------------------------

    target_col = "monthly_revenue"

    feature_columns = [
        "monthly_revenue_lag_1",
        "monthly_revenue_lag_2",
        "monthly_revenue_lag_3",
        "monthly_revenue_lag_6",
        "monthly_revenue_lag_12",
        "rolling_mean_3",
        "rolling_mean_6",
        "rolling_mean_12",
        "month",
        "year",
        "month_sin",
        "month_cos",
        "trend",
        "region_code",
        "model_code"
    ]

    X = feature_df[feature_columns]
    y = feature_df[target_col]

    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        shuffle=False
    )

    model = XGBRegressor(
        n_estimators=400,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42
    )

    model.fit(X_train, y_train)

    # ---------------------------------------------------------
    # 6. Evaluate on validation
    # ---------------------------------------------------------

    val_pred = model.predict(X_val)
    mae = mean_absolute_error(y_val, val_pred)
    rmse = np.sqrt(mean_squared_error(y_val, val_pred))

    print(f"Validation MAE: {mae:.2f}")
    print(f"Validation RMSE: {rmse:.2f}")

    # ---------------------------------------------------------
    # 7. Forecast next month
    # ---------------------------------------------------------

    def build_next_month_row(group: pd.DataFrame) -> pd.DataFrame:
        group = group.sort_values("sale_month").copy()

        last_row = group.iloc[-1]
        next_month = last_row["sale_month"] + pd.DateOffset(months=1)

        history = group["monthly_revenue"].tolist()
        lag_1 = history[-1] if len(history) >= 1 else 0
        lag_2 = history[-2] if len(history) >= 2 else 0
        lag_3 = history[-3] if len(history) >= 3 else 0
        lag_6 = history[-6] if len(history) >= 6 else 0
        lag_12 = history[-12] if len(history) >= 12 else 0

        rolling_3 = np.mean(history[-3:]) if len(history) >= 3 else np.mean(history)
        rolling_6 = np.mean(history[-6:]) if len(history) >= 6 else np.mean(history)
        rolling_12 = np.mean(history[-12:]) if len(history) >= 12 else np.mean(history)

        month = next_month.month

        next_row = pd.DataFrame([{
            "sale_month": next_month,
            "model": last_row["model"],
            "region": last_row["region"],
            "monthly_revenue_lag_1": lag_1,
            "monthly_revenue_lag_2": lag_2,
            "monthly_revenue_lag_3": lag_3,
            "monthly_revenue_lag_6": lag_6,
            "monthly_revenue_lag_12": lag_12,
            "rolling_mean_3": rolling_3,
            "rolling_mean_6": rolling_6,
            "rolling_mean_12": rolling_12,
            "month": month,
            "year": next_month.year,
            "month_sin": np.sin(2 * np.pi * month / 12),
            "month_cos": np.cos(2 * np.pi * month / 12),
            "trend": group["trend"].max() + 1,
            "region_code": last_row["region_code"],
            "model_code": last_row["model_code"],
        }])

        return next_row

    forecast_rows = []

    for (_, _), group in feature_df.groupby(["model", "region"]):
        next_row = build_next_month_row(group)
        forecast_rows.append(next_row)

    forecast_df = pd.concat(forecast_rows, ignore_index=True)
    forecast_df["forecast_revenue"] = model.predict(forecast_df[feature_columns])

    forecast_df = forecast_df[[
        "sale_month",
        "model",
        "region",
        "forecast_revenue"
    ]].rename(columns={
        "sale_month": "forecast_month",
        "forecast_revenue": "predicted_revenue"
    })

    forecast_df["created_at"] = pd.Timestamp.utcnow()

    forecast_df.to_csv(FORECAST_OUTPUT_PATH, index=False)
    print(f"Forecast saved to: {FORECAST_OUTPUT_PATH}")

    # ---------------------------------------------------------
    # 8. Display result
    # ---------------------------------------------------------

    print("\nForecast preview:")
    print(forecast_df.head(20).to_string(index=False))


if __name__ == "__main__":
    main()