"""Validation and basic data-quality rules for EV telemetry.

The validation layer checks that all required telemetry fields exist and
removes records that cannot participate in the analytics calculations.
"""

REQUIRED_COLUMNS = [
    "vehicle_id","model","region","timestamp","speed_kmh",
    "battery_percent","distance_km","temperature_c","charging"
]

def validate_columns(df):
    """Validate that every required telemetry column is present."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return True

def clean_basic(df):
    """Remove unusable rows and enforce basic telemetry value ranges."""
    df = df.dropna(subset=[
        "vehicle_id","model","region","timestamp",
        "speed_kmh","battery_percent","distance_km"
    ])
    return df[
        (df["speed_kmh"] >= 0) &
        (df["distance_km"] > 0) &
        (df["battery_percent"].between(0,100))
    ].copy()
