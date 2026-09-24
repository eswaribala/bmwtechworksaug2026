from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from xgboost import XGBRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed_features.csv"
)

ARTIFACTS_DIR = (
    PROJECT_ROOT
    / "artifacts"
)

MODEL_FILE = (
    ARTIFACTS_DIR
    / "best_model.pkl"
)

FEATURE_FILE = (
    ARTIFACTS_DIR
    / "feature_columns.pkl"
)


ARTIFACTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


df = pd.read_csv(DATA_FILE)

df["month"] = pd.to_datetime(
    df["month"]
)

print("Processed dataset loaded!")
print(f"Dataset shape: {df.shape}")


df = df.sort_values(
    "month"
).reset_index(
    drop=True
)


X = df.drop(
    columns=[
        "next_month_sales",
        "month"
    ]
)

y = df["next_month_sales"]


print()
print("Features prepared!")
print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")


unique_months = sorted(
    df["month"].unique()
)

total_months = len(
    unique_months
)

n_train_months = int(
    total_months * 0.80
)

train_months = unique_months[
    :n_train_months
]

test_months = unique_months[
    n_train_months:
]


train_mask = df["month"].isin(
    train_months
)

test_mask = df["month"].isin(
    test_months
)


X_train = X.loc[
    train_mask
]

X_test = X.loc[
    test_mask
]

y_train = y.loc[
    train_mask
]

y_test = y.loc[
    test_mask
]


print()
print("Chronological train/test split created!")
print(f"Total months   : {total_months}")
print(f"Training months: {len(train_months)}")
print(f"Testing months : {len(test_months)}")
print()
print(f"X_train: {X_train.shape}")
print(f"X_test : {X_test.shape}")
print(f"y_train: {y_train.shape}")
print(f"y_test : {y_test.shape}")


print()
print("Training period:")
print(
    f"{train_months[0]} to {train_months[-1]}"
)

print()
print("Testing period:")
print(
    f"{test_months[0]} to {test_months[-1]}"
)


print()
print("=" * 60)
print("TRAINING XGBOOST")
print("=" * 60)


xgboost_model = XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1,
    objective="reg:squarederror"
)


xgboost_model.fit(
    X_train,
    y_train
)


print()
print("XGBoost trained successfully!")


predictions = xgboost_model.predict(
    X_test
)


mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = mean_squared_error(
    y_test,
    predictions
) ** 0.5

r2 = r2_score(
    y_test,
    predictions
)


print()
print("=" * 60)
print("XGBOOST PERFORMANCE")
print("=" * 60)

print(f"MAE : {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R2  : {r2:.4f}")


joblib.dump(
    xgboost_model,
    MODEL_FILE
)


print()
print("XGBoost model saved to:")
print(MODEL_FILE)


feature_columns = X.columns.tolist()

joblib.dump(
    feature_columns,
    FEATURE_FILE
)


print()
print("Feature columns saved to:")
print(FEATURE_FILE)


sample_predictions = xgboost_model.predict(
    X_test.head(10)
)


sample_output = pd.DataFrame(
    {
        "Actual": y_test.head(10).values,
        "Predicted": sample_predictions,
    }
)


print()
print("Sample Predictions:")
print(
    sample_output.to_string(
        index=False
    )
)


print()
print("=" * 60)
print("XGBOOST MODEL TRAINING COMPLETED")
print("=" * 60)

print(f"Model file: {MODEL_FILE}")
print(f"Feature file: {FEATURE_FILE}")
print(f"MAE : {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R2  : {r2:.4f}")

print("=" * 60)