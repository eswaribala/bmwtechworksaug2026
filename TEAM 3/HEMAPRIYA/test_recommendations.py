from src.recommendation.recommendation_engine import (
    df,
    df_encoded,
    model,
    feature_columns,
)

import pandas as pd



latest_records = (
    df.sort_values("month")
    .groupby(
        ["dealer_id", "model"],
        as_index=False
    )
    .tail(1)
    .copy()
)


print()
print("=" * 80)
print("LATEST DEALER + MODEL RECORDS")
print("=" * 80)

print(
    f"Total dealer-model combinations: "
    f"{len(latest_records)}"
)



latest_indices = latest_records.index

encoded_latest = df_encoded.loc[
    latest_indices
].copy()



X = encoded_latest.drop(
    columns=[
        "next_month_sales",
        "month"
    ],
    errors="ignore"
)




X = X.reindex(
    columns=feature_columns,
    fill_value=0
)


print(
    f"Prediction input shape: {X.shape}"
)




print()
print("Predicting demand for all dealer-model combinations...")

predicted_demand = model.predict(X)

predicted_demand = pd.Series(
    predicted_demand,
    index=latest_records.index
).clip(
    lower=0
)




latest_records["predicted_demand"] = (
    predicted_demand
)


# 45 days of target inventory

latest_records["target_inventory"] = (
    latest_records["predicted_demand"]
    * 45
    / 30
)



latest_records["recommended_quantity"] = (
    latest_records["target_inventory"]
    -
    latest_records["current_inventory"]
)


latest_records["recommended_quantity"] = (
    latest_records["recommended_quantity"]
    .clip(lower=0)
    .round()
    .astype(int)
)



positive_cases = latest_records[
    latest_records["recommended_quantity"] > 0
].copy()


# Sort highest recommendation first

positive_cases = positive_cases.sort_values(
    "recommended_quantity",
    ascending=False
)




print()
print("=" * 80)
print("CASES WHERE ADDITIONAL INVENTORY IS RECOMMENDED")
print("=" * 80)


if positive_cases.empty:

    print()
    print("No positive recommendation cases found.")

else:

    display_columns = [
        "dealer_id",
        "model",
        "predicted_demand",
        "current_inventory",
        "target_inventory",
        "recommended_quantity",
    ]

    print(
        positive_cases[
            display_columns
        ]
        .head(20)
        .to_string(index=False)
    )




print()
print("=" * 80)

print(
    f"Total positive cases found: "
    f"{len(positive_cases)}"
)

print(
    f"Total dealer-model combinations checked: "
    f"{len(latest_records)}"
)

print("=" * 80)