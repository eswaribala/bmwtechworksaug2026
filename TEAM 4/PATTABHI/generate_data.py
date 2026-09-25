"""Generate realistic, referentially consistent BMW analytics sample data.

Usage:
    python generate_data.py
    python generate_data.py --output-dir data --seed 20260917

The generated files intentionally contain a small number of nullable analytical
attributes and exact duplicate rows for data-quality testing. Identifier columns
remain populated so joins between domains stay valid.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2026-09-01")
MODELS = ["X1", "X3", "X5", "X7", "i4", "iX", "i7"]
REGIONS = ["North", "South", "East", "West"]
CITIES = ["Bangalore", "Chennai", "Hyderabad", "Delhi", "Mumbai", "Pune", "Kolkata"]
FUEL_TYPES = {"X1": "Petrol", "X3": "Diesel", "X5": "Petrol", "X7": "Petrol", "i4": "Electric", "iX": "Electric", "i7": "Electric"}
MODEL_PRICES = {"X1": 5200000, "X3": 7000000, "X5": 10800000, "X7": 14000000, "i4": 7200000, "iX": 12500000, "i7": 20500000}
SERVICE_TYPES = ["Routine Service", "Brake Inspection", "Battery Health Check", "Software Update", "Annual Maintenance", "Recall Inspection"]
COMPONENTS = ["Battery", "Brake System", "Engine", "Transmission", "Infotainment", "Suspension", "Cooling System"]
FAULT_CODES = ["P0300", "P0420", "B0010", "C1234", "U0100", "E1101"]
FAILURE_CODES = ["BRK-001", "BAT-002", "ENG-003", "TRN-004", "ELE-005", "SUS-006"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--seed", type=int, default=20260917)
    return parser.parse_args()


def random_date(rng: np.random.Generator, start: pd.Timestamp = START_DATE, end: pd.Timestamp = END_DATE) -> pd.Timestamp:
    days = (end - start).days
    return start + pd.Timedelta(int(rng.integers(0, days + 1)), unit="D")


def random_region(rng: np.random.Generator) -> str:
    return str(rng.choice(REGIONS, p=[0.24, 0.29, 0.22, 0.25]))


def add_nulls(frame: pd.DataFrame, columns: list[str], fraction: float, rng: np.random.Generator) -> pd.DataFrame:
    result = frame.copy()
    for column in columns:
        count = max(1, int(len(result) * fraction))
        indices = rng.choice(result.index.to_numpy(), size=count, replace=False)
        result.loc[indices, column] = np.nan
    return result


def add_duplicates(frame: pd.DataFrame, count: int, rng: np.random.Generator) -> pd.DataFrame:
    duplicate_indices = rng.choice(frame.index.to_numpy(), size=count, replace=False)
    return pd.concat([frame, frame.loc[duplicate_indices]], ignore_index=True)


def build_dealers(rng: np.random.Generator, fake: Faker) -> pd.DataFrame:
    records = []
    for index in range(1, 121):
        region = random_region(rng)
        city_options = {
            "North": ["Delhi"],
            "South": ["Bangalore", "Chennai", "Hyderabad"],
            "East": ["Kolkata", "Hyderabad"],
            "West": ["Mumbai", "Pune"],
        }
        city = str(rng.choice(city_options[region]))
        records.append({
            "dealer_id": f"DLR-{index:04d}",
            "dealer_name": f"BMW {city} {fake.last_name()} Motors",
            "city": city,
            "region": region,
            "capacity": int(rng.integers(80, 301)),
            "rating": round(float(rng.uniform(3.7, 5.0)), 1),
        })
    return pd.DataFrame(records)


def build_vehicles(rng: np.random.Generator) -> pd.DataFrame:
    records = []
    for index in range(1, 251):
        model = str(rng.choice(MODELS, p=[0.18, 0.18, 0.16, 0.08, 0.15, 0.15, 0.10]))
        region = random_region(rng)
        vin = f"WBA{int(rng.integers(10**13, 10**14)):014d}"
        records.append({
            "vehicle_id": f"BMW-{index:05d}",
            "vin": vin,
            "model": model,
            "model_year": int(rng.choice([2024, 2025, 2026], p=[0.15, 0.55, 0.30])),
            "fuel_type": FUEL_TYPES[model],
            "region": region,
            "manufacturing_date": random_date(rng, START_DATE, pd.Timestamp("2026-06-30")).date().isoformat(),
        })
    return pd.DataFrame(records)


def build_sales(rng: np.random.Generator, vehicles: pd.DataFrame, dealers: pd.DataFrame, fake: Faker) -> pd.DataFrame:
    dealer_records = dealers.to_dict("records")
    vehicle_records = vehicles.to_dict("records")
    records = []
    for index in range(1, 361):
        vehicle = vehicle_records[int(rng.integers(0, len(vehicle_records)))]
        eligible = [dealer for dealer in dealer_records if dealer["region"] == vehicle["region"]]
        dealer = eligible[int(rng.integers(0, len(eligible)))]
        model = vehicle["model"]
        price = MODEL_PRICES[model] * float(rng.uniform(0.94, 1.10))
        records.append({
            "sale_id": f"SAL-{index:05d}",
            "vehicle_id": vehicle["vehicle_id"],
            "dealer_id": dealer["dealer_id"],
            "customer_id": f"CUS-{fake.unique.random_int(100000, 999999)}",
            "sale_date": random_date(rng).date().isoformat(),
            "model": model,
            "region": vehicle["region"],
            "price": round(price, 2),
            "quantity": int(rng.choice([1, 1, 1, 2])),
        })
    return pd.DataFrame(records)


def build_telemetry(rng: np.random.Generator, vehicles: pd.DataFrame) -> pd.DataFrame:
    vehicle_records = vehicles.to_dict("records")
    records = []
    for index in range(1, 481):
        vehicle = vehicle_records[int(rng.integers(0, len(vehicle_records)))]
        timestamp = random_date(rng) + pd.Timedelta(int(rng.integers(0, 1440)), unit="m")
        fault_code = str(rng.choice(FAULT_CODES)) if rng.random() < 0.075 else None
        records.append({
            "event_id": f"EVT-{index:06d}",
            "vehicle_id": vehicle["vehicle_id"],
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "speed": round(float(np.clip(rng.normal(48, 25), 0, 180)), 1),
            "battery_level": round(float(np.clip(rng.normal(68, 18), 8, 100)), 1),
            "temperature": round(float(np.clip(rng.normal(29, 8), 8, 52)), 1),
            "odometer": round(float(rng.uniform(500, 85000)), 1),
            "latitude": round(float(rng.uniform(8.0, 28.7)), 6),
            "longitude": round(float(rng.uniform(72.8, 80.3)), 6),
            "fault_code": fault_code,
        })
    return pd.DataFrame(records)


def build_maintenance(rng: np.random.Generator, vehicles: pd.DataFrame, dealers: pd.DataFrame) -> pd.DataFrame:
    dealer_records = dealers.to_dict("records")
    vehicle_records = vehicles.to_dict("records")
    records = []
    for index in range(1, 241):
        vehicle = vehicle_records[int(rng.integers(0, len(vehicle_records)))]
        eligible = [dealer for dealer in dealer_records if dealer["region"] == vehicle["region"]]
        dealer = eligible[int(rng.integers(0, len(eligible)))]
        parts_cost = float(rng.uniform(1500, 85000))
        labour_cost = float(rng.uniform(1000, 28000))
        has_failure = rng.random() < 0.18
        records.append({
            "service_id": f"SRV-{index:05d}",
            "vehicle_id": vehicle["vehicle_id"],
            "dealer_id": dealer["dealer_id"],
            "service_date": random_date(rng).date().isoformat(),
            "service_type": str(rng.choice(SERVICE_TYPES)),
            "odometer": round(float(rng.uniform(500, 85000)), 1),
            "parts_cost": round(parts_cost, 2),
            "labour_cost": round(labour_cost, 2),
            "failure_code": str(rng.choice(FAILURE_CODES)) if has_failure else None,
        })
    return pd.DataFrame(records)


def build_warranty(rng: np.random.Generator, vehicles: pd.DataFrame) -> pd.DataFrame:
    vehicle_records = vehicles.to_dict("records")
    records = []
    for index in range(1, 181):
        vehicle = vehicle_records[int(rng.integers(0, len(vehicle_records)))]
        status = str(rng.choice(["Open", "Approved", "Rejected", "Paid"], p=[0.18, 0.35, 0.12, 0.35]))
        records.append({
            "claim_id": f"CLM-{index:05d}",
            "vehicle_id": vehicle["vehicle_id"],
            "claim_date": random_date(rng).date().isoformat(),
            "component": str(rng.choice(COMPONENTS)),
            "claim_amount": round(float(rng.uniform(5000, 450000)), 2),
            "claim_status": status,
        })
    return pd.DataFrame(records)


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, date_format="%Y-%m-%d")
    print(f"Created {path} ({len(frame):,} rows)")


def generate(output_dir: Path, seed: int) -> dict[str, pd.DataFrame]:
    random.seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)
    fake = Faker("en_IN")
    fake.seed_instance(seed)
    output_dir.mkdir(parents=True, exist_ok=True)

    dealers = build_dealers(rng, fake)
    vehicles = build_vehicles(rng)
    sales = build_sales(rng, vehicles, dealers, fake)
    telemetry = build_telemetry(rng, vehicles)
    maintenance = build_maintenance(rng, vehicles, dealers)
    warranty = build_warranty(rng, vehicles)

    # Keep duplicates and nulls away from join keys so analytical joins remain valid.
    sales = add_nulls(sales, ["customer_id"], 0.01, rng)
    telemetry = add_nulls(telemetry, ["speed", "temperature", "fault_code"], 0.01, rng)
    maintenance = add_nulls(maintenance, ["failure_code"], 0.01, rng)
    warranty = add_nulls(warranty, ["component"], 0.01, rng)
    sales = add_duplicates(sales, 4, rng)
    telemetry = add_duplicates(telemetry, 5, rng)
    warranty = add_duplicates(warranty, 2, rng)

    datasets = {
        "vehicle_master.csv": vehicles,
        "sales.csv": sales,
        "dealer.csv": dealers,
        "telemetry.csv": telemetry,
        "maintenance.csv": maintenance,
        "warranty.csv": warranty,
    }
    for filename, frame in datasets.items():
        write_csv(frame, output_dir / filename)
    return datasets


def main() -> None:
    args = parse_args()
    generate(args.output_dir, args.seed)


if __name__ == "__main__":
    main()
