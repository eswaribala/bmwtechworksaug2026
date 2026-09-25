"""Schema definitions for BMW datasets."""

from __future__ import annotations

from typing import Any


VEHICLE_MASTER_COLUMNS = [
    "vehicle_id",
    "vin",
    "model",
    "model_year",
    "region",
    "dealer_id",
    "battery_capacity_kwh",
    "manufacture_date",
]

TELEMETRY_COLUMNS = [
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
]

SALES_COLUMNS = [
    "sale_id",
    "vehicle_id",
    "dealer_id",
    "model",
    "region",
    "sale_date",
    "sale_amount",
]

MAINTENANCE_COLUMNS = [
    "maintenance_id",
    "vehicle_id",
    "service_date",
    "service_type",
    "repair_cost",
    "dealer_id",
]

WARRANTY_COLUMNS = [
    "claim_id",
    "vehicle_id",
    "component",
    "claim_date",
    "claim_amount",
    "dealer_id",
]

DATASET_SCHEMAS = {
    "vehicle_master": VEHICLE_MASTER_COLUMNS,
    "telemetry": TELEMETRY_COLUMNS,
    "sales": SALES_COLUMNS,
    "maintenance": MAINTENANCE_COLUMNS,
    "warranty": WARRANTY_COLUMNS,
}


def normalize_column_names(columns: list[str]) -> list[str]:
    """Normalize names to snake_case and strip whitespace."""

    normalized: list[str] = []
    for column in columns:
        cleaned = str(column).strip().lower().replace(" ", "_")
        normalized.append(cleaned)
    return normalized


def validate_required_columns(dataset_name: str, actual_columns: list[Any]) -> None:
    """Validate that required columns exist for a dataset."""

    required = DATASET_SCHEMAS.get(dataset_name)
    if required is None:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    normalized_actual = normalize_column_names([str(value) for value in actual_columns])
    missing = [col for col in required if col not in normalized_actual]
    if missing:
        raise ValueError(f"Missing columns for {dataset_name}: {missing}")
