import pandas as pd
import pytest

from python.data_validation import validate_telemetry


def test_valid_telemetry():
    df = pd.DataFrame(
        {
            "vehicle_id": ["V001"],
            "model": ["iX"],
            "battery_level": [80],
            "temperature": [70],
            "speed": [60],
            "region": ["Chennai"],
            "event_timestamp": ["2026-09-17 10:00:00"],
        }
    )

    assert validate_telemetry(df) is True


def test_missing_vehicle_id():
    df = pd.DataFrame(
        {
            "vehicle_id": [None],
            "model": ["iX"],
            "battery_level": [80],
            "temperature": [70],
            "speed": [60],
            "region": ["Chennai"],
            "event_timestamp": ["2026-09-17 10:00:00"],
        }
    )

    with pytest.raises(ValueError):
        validate_telemetry(df)


def test_invalid_battery():
    df = pd.DataFrame(
        {
            "vehicle_id": ["V001"],
            "model": ["iX"],
            "battery_level": [150],
            "temperature": [70],
            "speed": [60],
            "region": ["Chennai"],
            "event_timestamp": ["2026-09-17 10:00:00"],
        }
    )

    with pytest.raises(ValueError):
        validate_telemetry(df)