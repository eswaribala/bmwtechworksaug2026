from pathlib import Path
import pandas as pd

from src.ingestion.ingest import load_csv
from src.validation.validate import validate_columns, clean_basic

ROOT = Path(__file__).resolve().parents[1]
df = load_csv(ROOT/"data/dataset.csv")
validate_columns(df)
df = clean_basic(df)

df["previous_battery"] = df.groupby("vehicle_id")["battery_percent"].shift(1)
df["battery_consumed"] = df["previous_battery"] - df["battery_percent"]

df["efficiency"] = (
    df["distance_km"] /
    df["battery_consumed"].where(df["battery_consumed"] > 0)
)

df["estimated_range_km"] = df["battery_percent"] * df["efficiency"]

out = ROOT/"data/curated_local"
out.mkdir(parents=True, exist_ok=True)

vehicle = (
    df.groupby(["vehicle_id","model","region"], as_index=False)
      .agg(
          total_distance_km=("distance_km","sum"),
          total_battery_consumed=(
              "battery_consumed",
              lambda x: x.clip(lower=0).sum()
          ),
          avg_speed_kmh=("speed_kmh","mean"),
          avg_temperature_c=("temperature_c","mean"),
          avg_estimated_range_km=("estimated_range_km","mean")
      )
)

vehicle["overall_efficiency"] = (
    vehicle["total_distance_km"] /
    vehicle["total_battery_consumed"].replace(0, pd.NA)
)

model = (
    vehicle.groupby("model", as_index=False)
    [["total_distance_km","total_battery_consumed"]].sum()
)
model["overall_efficiency"] = (
    model["total_distance_km"] /
    model["total_battery_consumed"].replace(0, pd.NA)
)

region = (
    vehicle.groupby("region", as_index=False)
    [["total_distance_km","total_battery_consumed"]].sum()
)
region["overall_efficiency"] = (
    region["total_distance_km"] /
    region["total_battery_consumed"].replace(0, pd.NA)
)

trend = (
    df.assign(date=df["timestamp"].dt.date)
      .groupby("date", as_index=False)
      .agg(
          avg_estimated_range_km=("estimated_range_km","mean"),
          avg_battery_percent=("battery_percent","mean")
      )
)

vehicle.sort_values("overall_efficiency", ascending=False).to_csv(out/"vehicle_efficiency.csv", index=False)
model.to_csv(out/"model_efficiency.csv", index=False)
region.to_csv(out/"region_efficiency.csv", index=False)
trend.to_csv(out/"range_trend.csv", index=False)
vehicle.nlargest(5, "overall_efficiency").to_csv(out/"top_vehicles.csv", index=False)
vehicle.nsmallest(5, "overall_efficiency").to_csv(out/"bottom_vehicles.csv", index=False)

print("Pipeline completed.")
print(f"Output: {out}")
