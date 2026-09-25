import pandas as pd

from bmw_data_lake.transformations import add_partition_columns, drop_duplicate_records, standardize_columns


def test_standardize_columns_lowercases_and_replaces_spaces():
    df = pd.DataFrame({"Vehicle ID": ["A"], "Battery Level": [10]})
    standardized = standardize_columns(df)

    assert list(standardized.columns) == ["vehicle_id", "battery_level"]


def test_add_partition_columns_adds_year_and_month():
    df = pd.DataFrame({"event_timestamp": ["2024-02-15 10:00:00", "2024-05-18 09:00:00"]})
    result = add_partition_columns(df)

    assert list(result["year"]) == [2024, 2024]
    assert list(result["month"]) == [2, 5]


def test_drop_duplicate_records_removes_repeats():
    df = pd.DataFrame({"vehicle_id": ["BMW1", "BMW1", "BMW2"], "battery_level": [80, 80, 60]})
    deduped = drop_duplicate_records(df, subset=["vehicle_id", "battery_level"])

    assert len(deduped) == 2
