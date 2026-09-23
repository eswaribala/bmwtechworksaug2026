from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/"data/curated_local"

def read(name):
    return pd.read_csv(DATA/name)

def summary():
    v = read("vehicle_efficiency.csv")
    return {
        "total_vehicles": int(v.vehicle_id.nunique()),
        "avg_efficiency": float(v.overall_efficiency.mean()),
        "avg_range": float(v.avg_estimated_range_km.mean()),
        "total_distance": float(v.total_distance_km.sum())
    }

def top_vehicles(limit=5):
    return read("vehicle_efficiency.csv").nlargest(
        limit, "overall_efficiency"
    ).to_dict("records")

def bottom_vehicles(limit=5):
    return read("vehicle_efficiency.csv").nsmallest(
        limit, "overall_efficiency"
    ).to_dict("records")

def models():
    return read("model_efficiency.csv").to_dict("records")

def regions():
    return read("region_efficiency.csv").to_dict("records")

def range_trend():
    return read("range_trend.csv").to_dict("records")
