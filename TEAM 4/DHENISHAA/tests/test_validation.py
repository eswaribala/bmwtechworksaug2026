import pandas as pd

from bmw_data_lake.validation import validate_dataframe


def test_validate_dataframe_keeps_valid_rows_and_rejects_invalid():
    df = pd.DataFrame(
        [
            {
                "vehicle_id": "BMW00001",
                "vin": "WBA12345678901234",
                "region": "Europe",
                "battery_level": 80,
                "battery_temperature": 30,
                "speed_kmh": 50,
                "event_timestamp": "2024-01-01 08:00:00",
            },
            {
                "vehicle_id": "",
                "vin": "BAD",
                "region": "Unknown",
                "battery_level": 110,
                "battery_temperature": 200,
                "speed_kmh": -10,
                "event_timestamp": "invalid",
            },
        ]
    )

    clean_df, rejected_df, summary = validate_dataframe(df, "telemetry")

    assert len(clean_df) == 1
    assert len(rejected_df) == 1
    assert summary["rejected_rows"] == 1
