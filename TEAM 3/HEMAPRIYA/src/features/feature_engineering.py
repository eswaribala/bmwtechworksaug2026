import pandas as pd
import numpy as np




df = pd.read_csv("data/dealer_inventory_features.csv")

print("Dataset loaded!")
print("Original shape:", df.shape)




df["month"] = pd.to_datetime(df["month"])




df = df.sort_values(
    ["dealer_id", "model", "month"]
).reset_index(drop=True)




df["sales_last_month"] = (
    df.groupby(["dealer_id", "model"])["sales"]
    .shift(1)
)



df["sales_3_month_avg"] = (
    df.groupby(["dealer_id", "model"])["sales"]
    .transform(
        lambda x: x.shift(1).rolling(3).mean()
    )
)




df["sales_6_month_avg"] = (
    df.groupby(["dealer_id", "model"])["sales"]
    .transform(
        lambda x: x.shift(1).rolling(6).mean()
    )
)




previous_previous_sales = (
    df.groupby(["dealer_id", "model"])["sales"]
    .shift(2)
)

df["sales_growth_1m"] = (
    (
        df["sales_last_month"]
        - previous_previous_sales
    )
    /
    previous_previous_sales.replace(0, np.nan)
)




df["regional_model_sales"] = (
    df.groupby(
        ["region", "model", "month"]
    )["sales"]
    .transform("mean")
)




daily_sales = df["sales_last_month"] / 30

df["days_of_inventory"] = (
    df["current_inventory"]
    /
    daily_sales.replace(0, np.nan)
)




df["inventory_turnover"] = (
    df["sales_last_month"]
    /
    df["current_inventory"].replace(0, np.nan)
)




df["month_number"] = (
    df["month"].dt.month
)




df["quarter"] = (
    df["month"].dt.quarter
)




print("\nMissing values before cleaning:")

print(
    df[
        [
            "sales_last_month",
            "sales_3_month_avg",
            "sales_6_month_avg",
            "sales_growth_1m",
            "regional_model_sales",
            "days_of_inventory",
            "inventory_turnover",
            "next_month_sales",
        ]
    ]
    .isna()
    .sum()
)



required_features = [
    "sales_last_month",
    "sales_3_month_avg",
    "sales_6_month_avg",
    "sales_growth_1m",
    "regional_model_sales",
    "days_of_inventory",
    "inventory_turnover",
    "next_month_sales",
]

df = df.dropna(
    subset=required_features
).reset_index(drop=True)




df = pd.get_dummies(
    df,
    columns=[
        "dealer_id",
        "model",
        "region"
    ],
    dtype=int
)



X = df.drop(
    columns=[
        "next_month_sales",
        "month"
    ]
)

y = df["next_month_sales"]


# -----------------------------------
# 17. Display results
# -----------------------------------

print("\nFeature engineering completed!")

print("\nFinal dataset shape:")
print(df.shape)

print("\nX shape:")
print(X.shape)

print("\ny shape:")
print(y.shape)

print("\nFeatures:")
print(X.columns.tolist())




output_file = "data/processed_features.csv"

df.to_csv(
    output_file,
    index=False
)

print("\nProcessed dataset saved to:")
print(output_file)