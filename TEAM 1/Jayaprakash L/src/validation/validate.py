REQUIRED_COLUMNS = [
    "vehicle_id","model","region","timestamp","speed_kmh",
    "battery_percent","distance_km","temperature_c","charging"
]

def validate_columns(df):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return True

def clean_basic(df):
    df = df.dropna(subset=[
        "vehicle_id","model","region","timestamp",
        "speed_kmh","battery_percent","distance_km"
    ])
    return df[
        (df["speed_kmh"] >= 0) &
        (df["distance_km"] > 0) &
        (df["battery_percent"].between(0,100))
    ].copy()
