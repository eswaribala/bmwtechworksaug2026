from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ValidationResult:
    valid: pd.DataFrame
    rejected: pd.DataFrame
    errors: dict[str, int]


def validate_telemetry(frame: pd.DataFrame) -> ValidationResult:
    required = {"event_id", "vehicle_id", "timestamp", "battery_level", "temperature"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing telemetry columns: {sorted(missing)}")

    invalid = frame[list(required)].isna().any(axis=1)
    invalid |= pd.to_datetime(frame["timestamp"], errors="coerce").isna()
    invalid |= ~frame["battery_level"].between(0, 100, inclusive="both")
    invalid |= frame["temperature"].lt(-50) | frame["temperature"].gt(150)
    invalid |= frame.duplicated(subset=["event_id"], keep="first")
    errors = {"invalid_records": int(invalid.sum())}
    return ValidationResult(frame.loc[~invalid].copy(), frame.loc[invalid].copy(), errors)


def validate_required_columns(frame: pd.DataFrame, columns: list[str]) -> ValidationResult:
    missing = set(columns).difference(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    invalid = frame[columns].isna().any(axis=1) | frame.duplicated(keep="first")
    return ValidationResult(
        valid=frame.loc[~invalid].copy(),
        rejected=frame.loc[invalid].copy(),
        errors={"invalid_records": int(invalid.sum())},
    )


def validate_vehicle_references(frame: pd.DataFrame, vehicle_ids: set[str]) -> ValidationResult:
    if "vehicle_id" not in frame.columns:
        raise ValueError("Missing columns: ['vehicle_id']")
    invalid = frame["vehicle_id"].isna() | ~frame["vehicle_id"].isin(vehicle_ids)
    return ValidationResult(
        valid=frame.loc[~invalid].copy(),
        rejected=frame.loc[invalid].copy(),
        errors={"invalid_vehicle_ids": int(invalid.sum())},
    )
