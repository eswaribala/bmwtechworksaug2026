from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "dealer_inventory_features.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "artifacts"
    / "best_model.pkl"
)

FEATURE_COLUMNS_FILE = (
    PROJECT_ROOT
    / "artifacts"
    / "feature_columns.pkl"
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

model = joblib.load(MODEL_FILE)

feature_columns = joblib.load(
    FEATURE_COLUMNS_FILE
)

print("Model loaded successfully!")


# ============================================================
# LOAD RAW DATA
# ============================================================

df = pd.read_csv(DATA_FILE)

df["month"] = pd.to_datetime(df["month"])

# Sort exactly like feature engineering
df = df.sort_values(
    ["dealer_id", "model", "month"]
).reset_index(drop=True)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

# ------------------------------------------------------------
# 1. Previous month sales
# ------------------------------------------------------------

df["sales_last_month"] = (
    df.groupby(
        ["dealer_id", "model"]
    )["sales"]
    .shift(1)
)


# ------------------------------------------------------------
# 2. Previous 3-month average
# ------------------------------------------------------------

df["sales_3_month_avg"] = (
    df.groupby(
        ["dealer_id", "model"]
    )["sales"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(3)
        .mean()
    )
)


# ------------------------------------------------------------
# 3. Previous 6-month average
# ------------------------------------------------------------

df["sales_6_month_avg"] = (
    df.groupby(
        ["dealer_id", "model"]
    )["sales"]
    .transform(
        lambda x:
        x.shift(1)
        .rolling(6)
        .mean()
    )
)


# ------------------------------------------------------------
# 4. Sales growth
# ------------------------------------------------------------

previous_previous_sales = (
    df.groupby(
        ["dealer_id", "model"]
    )["sales"]
    .shift(2)
)

df["sales_growth_1m"] = (
    (
        df["sales_last_month"]
        - previous_previous_sales
    )
    /
    previous_previous_sales.replace(
        0,
        np.nan
    )
)


# ------------------------------------------------------------
# 5. Regional model sales
# ------------------------------------------------------------

df["regional_model_sales"] = (
    df.groupby(
        ["region", "model", "month"]
    )["sales"]
    .transform("mean")
)


# ------------------------------------------------------------
# 6. Days of inventory
# ------------------------------------------------------------

daily_sales = (
    df["sales_last_month"] / 30
)

df["days_of_inventory"] = (
    df["current_inventory"]
    /
    daily_sales.replace(
        0,
        np.nan
    )
)


# ------------------------------------------------------------
# 7. Inventory turnover
# ------------------------------------------------------------

df["inventory_turnover"] = (
    df["sales_last_month"]
    /
    df["current_inventory"].replace(
        0,
        np.nan
    )
)


# ------------------------------------------------------------
# 8. Month number
# ------------------------------------------------------------

df["month_number"] = (
    df["month"].dt.month
)


# ------------------------------------------------------------
# 9. Quarter
# ------------------------------------------------------------

df["quarter"] = (
    df["month"].dt.quarter
)


# ============================================================
# REMOVE ROWS WITHOUT ENOUGH HISTORY
# ============================================================

required_columns = [
    "sales_last_month",
    "sales_3_month_avg",
    "sales_6_month_avg",
    "sales_growth_1m",
    "days_of_inventory",
    "inventory_turnover",
]

df = df.dropna(
    subset=required_columns
).copy()


# ============================================================
# ONE-HOT ENCODING
# ============================================================

df_encoded = pd.get_dummies(
    df,
    columns=[
        "dealer_id",
        "model",
        "region"
    ],
    dtype=int
)


# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

def recommend_inventory(
    dealer_id,
    model_name
):
    """
    Generate an inventory recommendation
    for one dealer and one BMW model.
    """

    # ========================================================
    # 1. FIND DEALER + MODEL
    # ========================================================

    selected = df[
        (df["dealer_id"] == dealer_id)
        &
        (df["model"] == model_name)
    ].copy()

    if selected.empty:
        raise ValueError(
            f"No data found for dealer "
            f"{dealer_id} and model "
            f"{model_name}."
        )


    # ========================================================
    # 2. GET LATEST AVAILABLE MONTH
    # ========================================================

    selected = selected.sort_values(
        "month"
    )

    latest = selected.iloc[-1]

    current_inventory = float(
        latest["current_inventory"]
    )


    # ========================================================
    # 3. GET EXACT SAME ROW FROM ENCODED DATA
    # ========================================================

    latest_index = latest.name

    encoded_selected = df_encoded.loc[
        [latest_index]
    ].copy()

    if encoded_selected.empty:
        raise ValueError(
            "Encoded feature row not found."
        )


    # ========================================================
    # 4. PREPARE INPUT FOR MODEL
    # ========================================================

    X_input = encoded_selected.drop(
        columns=[
            "next_month_sales",
            "month"
        ],
        errors="ignore"
    )


    # Make sure prediction columns are exactly
    # the same as the training columns.

    X_input = X_input.reindex(
        columns=feature_columns,
        fill_value=0
    )


    # ========================================================
    # 5. PREDICT NEXT MONTH DEMAND
    # ========================================================

    predicted_demand = model.predict(
        X_input
    )[0]

    # Demand cannot be negative.

    predicted_demand = float(
        max(
            0,
            predicted_demand
        )
    )


    # ========================================================
    # 6. CALCULATE TARGET INVENTORY
    # ========================================================

    # Business rule:
    #
    # Maintain 45 days of inventory.
    #
    # 30 days = approximately one month
    # 45 days = 1.5 months

    target_inventory = float(
        predicted_demand
        * 45
        / 30
    )


    # ========================================================
    # 7. CALCULATE RECOMMENDED QUANTITY
    # ========================================================

    recommended_quantity = (
        target_inventory
        - current_inventory
    )

    # Never recommend a negative quantity.

    recommended_quantity = max(
        0,
        recommended_quantity
    )

    recommended_quantity = int(
        round(
            recommended_quantity
        )
    )


    # ========================================================
    # 8. GET BUSINESS INFORMATION
    # ========================================================

    sales_last_month = float(
        latest["sales_last_month"]
    )

    sales_3_month_avg = float(
        latest["sales_3_month_avg"]
    )

    sales_6_month_avg = float(
        latest["sales_6_month_avg"]
    )

    days_of_inventory = float(
        latest["days_of_inventory"]
    )


    # ========================================================
    # 9. DETERMINE SALES TREND
    # ========================================================

    if sales_last_month > (
        sales_3_month_avg * 1.10
    ):

        sales_trend = "increasing"

    elif sales_last_month < (
        sales_3_month_avg * 0.90
    ):

        sales_trend = "decreasing"

    else:

        sales_trend = "stable"


    # ========================================================
    # 10. CALCULATE DEMAND CHANGE
    # ========================================================

    if sales_3_month_avg > 0:

        demand_change_pct = (
            (
                sales_last_month
                - sales_3_month_avg
            )
            /
            sales_3_month_avg
        ) * 100

    else:

        demand_change_pct = 0.0


    # ========================================================
    # 11. DETERMINE INVENTORY STATUS
    # ========================================================

    if days_of_inventory < 30:

        inventory_status = "low"

    elif days_of_inventory > 60:

        inventory_status = "high"

    else:

        inventory_status = "adequate"


    # ========================================================
    # 12. CALCULATE INVENTORY GAP
    # ========================================================

    inventory_gap = (
        target_inventory
        - current_inventory
    )


    # ========================================================
    # 13. GENERATE BUSINESS REASON
    # ========================================================

    # --------------------------------------------------------
    # CASE A:
    # Additional inventory is recommended
    # --------------------------------------------------------

    if recommended_quantity > 0:

        # ----------------------------------------------------
        # Increasing demand + low inventory
        # ----------------------------------------------------

        if (
            sales_trend == "increasing"
            and inventory_status == "low"
        ):

            reason = (
                f"Demand is increasing by approximately "
                f"{abs(demand_change_pct):.1f}% compared "
                f"with the recent 3-month average. "
                f"Current inventory is only "
                f"{current_inventory:.0f} vehicles, "
                f"below the target level of "
                f"{target_inventory:.1f}. "
                f"Recommend stocking "
                f"{recommended_quantity} additional vehicles."
            )


        # ----------------------------------------------------
        # Increasing demand + adequate inventory
        # ----------------------------------------------------

        elif sales_trend == "increasing":

            reason = (
                f"Demand is increasing by approximately "
                f"{abs(demand_change_pct):.1f}% compared "
                f"with the recent 3-month average. "
                f"Current inventory of "
                f"{current_inventory:.0f} vehicles is "
                f"below the target level of "
                f"{target_inventory:.1f}. "
                f"Recommend adding "
                f"{recommended_quantity} vehicles "
                f"to maintain sufficient stock."
            )


        # ----------------------------------------------------
        # Decreasing demand but inventory below target
        # ----------------------------------------------------

        elif sales_trend == "decreasing":

            reason = (
                f"Demand is decreasing by approximately "
                f"{abs(demand_change_pct):.1f}% compared "
                f"with the recent 3-month average. "
                f"However, current inventory of "
                f"{current_inventory:.0f} vehicles remains "
                f"below the target level of "
                f"{target_inventory:.1f}. "
                f"Recommend a limited replenishment of "
                f"{recommended_quantity} vehicles."
            )


        # ----------------------------------------------------
        # Stable demand + inventory below target
        # ----------------------------------------------------

        else:

            reason = (
                f"Demand is relatively stable compared "
                f"with the recent 3-month average. "
                f"Current inventory of "
                f"{current_inventory:.0f} vehicles is "
                f"below the target level of "
                f"{target_inventory:.1f}. "
                f"Recommend stocking "
                f"{recommended_quantity} additional vehicles."
            )


    # --------------------------------------------------------
    # CASE B:
    # No additional inventory is recommended
    # --------------------------------------------------------

    else:

        # ----------------------------------------------------
        # Decreasing demand + high inventory
        # ----------------------------------------------------

        if (
            sales_trend == "decreasing"
            and inventory_status == "high"
        ):

            reason = (
                f"Demand is decreasing by approximately "
                f"{abs(demand_change_pct):.1f}% compared "
                f"with the recent 3-month average, while "
                f"current inventory is high at "
                f"{current_inventory:.0f} vehicles. "
                f"Inventory provides approximately "
                f"{days_of_inventory:.1f} days of coverage "
                f"and is above the target level of "
                f"{target_inventory:.1f}. "
                f"No additional stock is recommended."
            )


        # ----------------------------------------------------
        # Decreasing demand + adequate inventory
        # ----------------------------------------------------

        elif sales_trend == "decreasing":

            reason = (
                f"Demand is decreasing by approximately "
                f"{abs(demand_change_pct):.1f}% compared "
                f"with the recent 3-month average. "
                f"Current inventory of "
                f"{current_inventory:.0f} vehicles provides "
                f"{days_of_inventory:.1f} days of coverage "
                f"and is sufficient for the expected demand. "
                f"No additional stock is recommended."
            )


        # ----------------------------------------------------
        # Increasing demand + inventory already sufficient
        # ----------------------------------------------------

        elif sales_trend == "increasing":

            reason = (
                f"Demand is increasing by approximately "
                f"{abs(demand_change_pct):.1f}% compared "
                f"with the recent 3-month average. "
                f"However, current inventory of "
                f"{current_inventory:.0f} vehicles is already "
                f"above the target level of "
                f"{target_inventory:.1f}. "
                f"No additional stock is currently required."
            )


        # ----------------------------------------------------
        # Stable demand + sufficient inventory
        # ----------------------------------------------------

        else:

            reason = (
                f"Demand is relatively stable compared "
                f"with the recent 3-month average. "
                f"Current inventory of "
                f"{current_inventory:.0f} vehicles is "
                f"above the target level of "
                f"{target_inventory:.1f}. "
                f"No additional stock is currently required."
            )


    # ========================================================
    # 14. FINAL OUTPUT
    # ========================================================

    result = {

        "Dealer":
            dealer_id,

        "Model":
            model_name,

        "Recommended Quantity":
            recommended_quantity,

        "Predicted Next Month Demand":
            float(
                round(
                    predicted_demand,
                    2
                )
            ),

        "Current Inventory":
            float(
                round(
                    current_inventory,
                    2
                )
            ),

        "Target Inventory":
            float(
                round(
                    target_inventory,
                    2
                )
            ),

        "Days of Inventory":
            float(
                round(
                    days_of_inventory,
                    2
                )
            ),

        "Sales Trend":
            sales_trend,

        "Reason":
            reason
    }


    return result


# ============================================================
# TEST THE RECOMMENDATION ENGINE
# ============================================================

if __name__ == "__main__":

    test_cases = [
        ("D001", "i4"),
        ("D002", "X5"),
        ("D003", "3 Series"),
        ("D004", "X3"),
        ("D005", "iX"),
    ]


    print()
    print("=" * 70)
    print("BMW DEALER INVENTORY RECOMMENDATIONS")
    print("=" * 70)


    for dealer_id, model_name in test_cases:

        try:

            result = recommend_inventory(
                dealer_id=dealer_id,
                model_name=model_name
            )

            print()
            print("-" * 70)

            for key, value in result.items():

                print(
                    f"{key}: {value}"
                )


        except Exception as e:

            print()
            print(
                f"Error for "
                f"{dealer_id} + "
                f"{model_name}: {e}"
            )


    print()
    print("=" * 70)