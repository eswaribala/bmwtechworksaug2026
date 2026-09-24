import numpy as np
import pandas as pd
from pathlib import Path




PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)




NUM_DEALERS = 250
NUM_MONTHS = 60

DEALERS = [
    f"D{str(i).zfill(3)}"
    for i in range(1, NUM_DEALERS + 1)
]

MODELS = [
    "2 Series",
    "3 Series",
    "4 Series",
    "5 Series",
    "7 Series",
    "X1",
    "X3",
    "X5",
    "X7",
    "i4",
    "i5",
    "i7",
    "iX",
    "iX1",
    "iX3",
]

REGIONS = [
    "North",
    "South",
    "East",
    "West",
    "Central",
]



rng = np.random.default_rng(42)




dealer_regions = {}

for dealer in DEALERS:
    dealer_regions[dealer] = rng.choice(REGIONS)



model_base_demand = {
    "2 Series": 18,
    "3 Series": 25,
    "4 Series": 20,
    "5 Series": 28,
    "7 Series": 12,
    "X1": 32,
    "X3": 38,
    "X5": 30,
    "X7": 18,
    "i4": 22,
    "i5": 24,
    "i7": 10,
    "iX": 20,
    "iX1": 27,
    "iX3": 25,
}




region_multiplier = {
    "North": 1.00,
    "South": 1.15,
    "East": 0.90,
    "West": 1.25,
    "Central": 0.95,
}




records = []

start_date = pd.Timestamp("2021-01-01")


for dealer in DEALERS:

 

    region = dealer_regions[dealer]

    # Each dealer has its own demand level
    dealer_multiplier = rng.uniform(
        0.75,
        1.30
    )

    for model in MODELS:

     

        base_demand = model_base_demand[model]

        # Dealer-model specific variation
        dealer_model_multiplier = rng.uniform(
            0.80,
            1.20
        )

        # Start with some initial inventory
        inventory = None

        previous_sales = None

        for month_number in range(NUM_MONTHS):

    

            date = (
                start_date
                + pd.DateOffset(
                    months=month_number
                )
            )

            month = date.strftime("%Y-%m")

            month_number_in_year = date.month


         

            seasonal_effect = {
                1: 0.90,
                2: 0.92,
                3: 1.00,
                4: 1.05,
                5: 1.08,
                6: 1.00,
                7: 0.98,
                8: 1.02,
                9: 1.08,
                10: 1.15,
                11: 1.20,
                12: 1.10,
            }[
                month_number_in_year
            ]



            growth_effect = (
                1
                + (month_number * 0.003)
            )



            expected_demand = (
                base_demand
                * region_multiplier[region]
                * dealer_multiplier
                * dealer_model_multiplier
                * seasonal_effect
                * growth_effect
            )


       

            sales = max(
                1,
                int(
                    rng.normal(
                        loc=expected_demand,
                        scale=max(
                            expected_demand * 0.12,
                            1
                        )
                    )
                )
            )



            if previous_sales is None:

                previous_month_sales = sales

            else:

                previous_month_sales = previous_sales


        

            if inventory is None:

             

                inventory = int(
                    sales
                    * rng.uniform(
                        1.2,
                        1.8
                    )
                )

            else:

               
                inventory_after_sales = (
                    inventory
                    - previous_sales
                )

                inventory_after_sales = max(
                    inventory_after_sales,
                    0
                )


               

                replenishment = int(
                    previous_sales
                    * rng.uniform(
                        0.80,
                        1.30
                    )
                )

                replenishment = max(
                    replenishment,
                    5
                )


             

                inventory = (
                    inventory_after_sales
                    + replenishment
                )


            

            if month_number == 0:

                inventory_30_days_ago = inventory

            else:

                inventory_30_days_ago = max(
                    inventory
                    + rng.integers(
                        -5,
                        6
                    ),
                    1
                )



            records.append(
                {
                    "dealer_id": dealer,
                    "model": model,
                    "region": region,
                    "month": month,
                    "sales": sales,
                    "current_inventory": inventory,
                    "previous_month_sales": previous_month_sales,
                    "inventory_30_days_ago": inventory_30_days_ago,
                }
            )



            previous_sales = sales




df = pd.DataFrame(records)



df["next_month_sales"] = (
    df.groupby(
        ["dealer_id", "model"]
    )["sales"]
    .shift(-1)
)



df = df.dropna(
    subset=["next_month_sales"]
).reset_index(
    drop=True
)


df["next_month_sales"] = (
    df["next_month_sales"]
    .astype(int)
)




output_file = (
    DATA_DIR
    / "dealer_inventory_features.csv"
)

df.to_csv(
    output_file,
    index=False
)




print(
    "\nDataset generated successfully!"
)

print(
    "\nDataset shape:"
)

print(
    df.shape
)


print(
    "\nColumns:"
)

print(
    df.columns.tolist()
)


print(
    "\nFirst 10 rows:"
)

print(
    df.head(10)
)


print(
    "\nNumber of dealers:"
)

print(
    df["dealer_id"].nunique()
)


print(
    "\nNumber of models:"
)

print(
    df["model"].nunique()
)


print(
    "\nNumber of regions:"
)

print(
    df["region"].nunique()
)


print(
    "\nNumber of months:"
)

print(
    df["month"].nunique()
)


print(
    "\nInventory statistics:"
)

print(
    df["current_inventory"].describe()
)


print(
    "\nNumber of zero-inventory rows:"
)

print(
    (df["current_inventory"] == 0).sum()
)


print(
    "\nSaved to:"
)

print(
    output_file
)