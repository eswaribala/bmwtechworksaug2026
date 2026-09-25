"""Synthetic BMW data generator for the serverless data lake project."""

from __future__ import annotations

import csv
from pathlib import Path
from random import Random

from .config import DEFAULT_GENERATED_DIR, DEFAULT_SAMPLE_DIR


def generate_vehicle_master(output_dir: str | Path = DEFAULT_GENERATED_DIR, seed: int = 42) -> Path:
    """Generate a synthetic vehicle master dataset."""

    rng = Random(seed)
    output_path = Path(output_dir) / "vehicle_master.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    regions = ["North America", "Europe", "Asia Pacific", "Middle East"]
    models = ["i3", "i4", "iX3", "iX5", "X5", "X7"]
    vehicles = []
    for idx in range(1, 251):
        vehicles.append(
            {
                "vehicle_id": f"BMW{idx:05d}",
                "vin": f"WBA{rng.randint(100000000, 999999999):09d}",
                "model": rng.choice(models),
                "model_year": rng.randint(2020, 2025),
                "region": rng.choice(regions),
                "dealer_id": f"DLR{rng.randint(100, 999)}",
                "battery_capacity_kwh": round(rng.uniform(50.0, 120.0), 2),
                "manufacture_date": f"202{rng.randint(0, 5)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
            }
        )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "vehicle_id",
                "vin",
                "model",
                "model_year",
                "region",
                "dealer_id",
                "battery_capacity_kwh",
                "manufacture_date",
            ],
        )
        writer.writeheader()
        writer.writerows(vehicles)

    return output_path


def generate_telemetry(output_dir: str | Path = DEFAULT_GENERATED_DIR, seed: int = 42, rows: int = 5000) -> Path:
    """Generate a telemetry dataset with realistic values and invalid samples."""

    rng = Random(seed)
    output_path = Path(output_dir) / "telemetry.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    regions = ["North America", "Europe", "Asia Pacific", "Middle East"]
    faults = ["P0", "P1", "P2", "P3", "E21", "E42", "B17", "C09", "None"]
    rows_data = []

    for idx in range(rows):
        event_year = 2024
        event_month = rng.randint(1, 12)
        event_day = rng.randint(1, 28)
        region = rng.choice(regions)
        base_vehicle = f"BMW{rng.randint(1, 250):05d}"
        battery_level = round(rng.uniform(10, 100), 2)
        battery_temperature = round(rng.uniform(-10, 75), 2)
        engine_temperature = round(rng.uniform(60, 120), 2)
        rows_data.append(
            {
                "vehicle_id": base_vehicle,
                "event_timestamp": f"{event_year}-{event_month:02d}-{event_day:02d} 08:{rng.randint(0, 59):02d}:00",
                "event_date": f"{event_year}-{event_month:02d}-{event_day:02d}",
                "year": event_year,
                "month": event_month,
                "region": region,
                "speed_kmh": round(rng.uniform(0, 220), 2),
                "battery_level": battery_level,
                "battery_temperature": battery_temperature,
                "engine_temperature": engine_temperature,
                "latitude": round(rng.uniform(20, 60), 6),
                "longitude": round(rng.uniform(-120, 60), 6),
                "fault_code": rng.choice(faults),
            }
        )

    invalid_rows = [
        {
            "vehicle_id": "",
            "event_timestamp": "invalid-date",
            "event_date": "",
            "year": "not-a-year",
            "month": 99,
            "region": "Unknown",
            "speed_kmh": -10,
            "battery_level": 150,
            "battery_temperature": 200,
            "engine_temperature": -50,
            "latitude": "bad",
            "longitude": "bad",
            "fault_code": "",
        },
        {
            "vehicle_id": "BMW99999",
            "event_timestamp": "2024-05-12 05:30:00",
            "event_date": "2024-05-12",
            "year": 2024,
            "month": 5,
            "region": "Europe",
            "speed_kmh": 55,
            "battery_level": 88,
            "battery_temperature": 36,
            "engine_temperature": 95,
            "latitude": 50.2,
            "longitude": 13.4,
            "fault_code": "P1",
        },
    ]
    rows_data.extend(invalid_rows)

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "vehicle_id",
                "event_timestamp",
                "event_date",
                "year",
                "month",
                "region",
                "speed_kmh",
                "battery_level",
                "battery_temperature",
                "engine_temperature",
                "latitude",
                "longitude",
                "fault_code",
            ],
        )
        writer.writeheader()
        writer.writerows(rows_data)

    return output_path


def generate_sales(output_dir: str | Path = DEFAULT_GENERATED_DIR, seed: int = 42) -> Path:
    """Generate a sales dataset."""

    rng = Random(seed)
    output_path = Path(output_dir) / "sales.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    regions = ["North America", "Europe", "Asia Pacific", "Middle East"]
    models = ["i3", "i4", "iX3", "iX5", "X5", "X7"]
    sales = []
    for idx in range(1, 301):
        sales.append(
            {
                "sale_id": f"SALE{idx:05d}",
                "vehicle_id": f"BMW{rng.randint(1, 250):05d}",
                "dealer_id": f"DLR{rng.randint(100, 999)}",
                "model": rng.choice(models),
                "region": rng.choice(regions),
                "sale_date": f"202{rng.randint(0, 5)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "sale_amount": round(rng.uniform(25000, 95000), 2),
            }
        )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["sale_id", "vehicle_id", "dealer_id", "model", "region", "sale_date", "sale_amount"],
        )
        writer.writeheader()
        writer.writerows(sales)

    return output_path


def generate_maintenance(output_dir: str | Path = DEFAULT_GENERATED_DIR, seed: int = 42) -> Path:
    """Generate a maintenance dataset."""

    rng = Random(seed)
    output_path = Path(output_dir) / "maintenance.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    services = ["battery_check", "brake_service", "tire_rotation", "software_update", "inspection"]
    records = []
    for idx in range(1, 201):
        records.append(
            {
                "maintenance_id": f"MNT{idx:05d}",
                "vehicle_id": f"BMW{rng.randint(1, 250):05d}",
                "service_date": f"202{rng.randint(0, 5)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "service_type": rng.choice(services),
                "repair_cost": round(rng.uniform(120, 2900), 2),
                "dealer_id": f"DLR{rng.randint(100, 999)}",
            }
        )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["maintenance_id", "vehicle_id", "service_date", "service_type", "repair_cost", "dealer_id"],
        )
        writer.writeheader()
        writer.writerows(records)

    return output_path


def generate_warranty(output_dir: str | Path = DEFAULT_GENERATED_DIR, seed: int = 42) -> Path:
    """Generate a warranty claims dataset."""

    rng = Random(seed)
    output_path = Path(output_dir) / "warranty.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    components = ["battery", "motor", "hvac", "software", "brake_system"]
    records = []
    for idx in range(1, 181):
        records.append(
            {
                "claim_id": f"CLAIM{idx:05d}",
                "vehicle_id": f"BMW{rng.randint(1, 250):05d}",
                "component": rng.choice(components),
                "claim_date": f"202{rng.randint(0, 5)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
                "claim_amount": round(rng.uniform(400, 6000), 2),
                "dealer_id": f"DLR{rng.randint(100, 999)}",
            }
        )

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["claim_id", "vehicle_id", "component", "claim_date", "claim_amount", "dealer_id"],
        )
        writer.writeheader()
        writer.writerows(records)

    return output_path


def generate_all_datasets(output_dir: str | Path = DEFAULT_GENERATED_DIR, seed: int = 42) -> dict[str, Path]:
    """Generate all BMW sample datasets."""

    return {
        "vehicle_master": generate_vehicle_master(output_dir, seed=seed),
        "telemetry": generate_telemetry(output_dir, seed=seed, rows=15000),
        "sales": generate_sales(output_dir, seed=seed),
        "maintenance": generate_maintenance(output_dir, seed=seed),
        "warranty": generate_warranty(output_dir, seed=seed),
    }


def create_sample_data_copy() -> dict[str, Path]:
    """Create a copy of the generated data in the sample directory for documentation use."""

    sample_dir = Path(DEFAULT_SAMPLE_DIR)
    sample_dir.mkdir(parents=True, exist_ok=True)
    generated = generate_all_datasets(DEFAULT_GENERATED_DIR, seed=7)
    sample_files = {}
    for name, path in generated.items():
        target = sample_dir / path.name
        target.write_bytes(path.read_bytes())
        sample_files[name] = target
    return sample_files
