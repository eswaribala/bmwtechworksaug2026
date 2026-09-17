"""
Test: Null detection, VIN validation, date validation, schema check
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.processing.validator import (
    check_nulls, check_vin, check_dates, check_schema, null_summary
)


# ─── Null detection ───────────────────────────────────────────
def test_null_detection_flags_missing_vehicle_id(spark):
    df = spark.createDataFrame(
        [(None, 'WBA' + 'A' * 14, '2026-01-01'), ('BMW001', 'WBA' + 'B' * 14, '2026-01-02')],
        ['vehicle_id', 'vin', 'timestamp'],
    )
    result = check_nulls(df, 'telemetry').toPandas()
    assert result['__null_fail'].iloc[0] == True
    assert result['__null_fail'].iloc[1] == False


def test_null_detection_clean_row_passes(spark):
    df = spark.createDataFrame(
        [('BMW001', 'WBA' + 'A' * 14, '2026-01-01')],
        ['vehicle_id', 'vin', 'timestamp'],
    )
    result = check_nulls(df, 'telemetry').toPandas()
    assert result['__null_fail'].iloc[0] == False


def test_null_summary_returns_correct_counts(spark):
    df = spark.createDataFrame(
        [(None, 'WBA' + 'A' * 14), ('BMW001', None), (None, 'WBA' + 'C' * 14)],
        ['vehicle_id', 'vin'],
    )
    summary = null_summary(df, 'vehicle_master')
    vid = next(s for s in summary if s['column'] == 'vehicle_id')
    assert vid['null_count'] == 2
    assert abs(vid['null_pct'] - 66.67) < 1


# ─── VIN validation ───────────────────────────────────────────
def test_vin_valid_17_char_accepted(spark):
    df = spark.createDataFrame([('WBA00000000000001',)], ['vin'])
    result = check_vin(df).toPandas()
    assert result['__vin_fail'].iloc[0] == False


def test_vin_invalid_short_rejected(spark):
    df = spark.createDataFrame([('SHORT',)], ['vin'])
    result = check_vin(df).toPandas()
    assert result['__vin_fail'].iloc[0] == True


def test_vin_null_rejected(spark):
    df = spark.createDataFrame([(None,)], schema='vin STRING')
    result = check_vin(df).toPandas()
    assert result['__vin_fail'].iloc[0] == True


def test_vin_contains_i_o_q_rejected(spark):
    # I, O, Q are not valid in VINs
    df = spark.createDataFrame([('WBA0000000000000I',)], ['vin'])
    result = check_vin(df).toPandas()
    assert result['__vin_fail'].iloc[0] == True


# ─── Date validation ──────────────────────────────────────────
def test_date_valid_iso_passes(spark):
    df = spark.createDataFrame([('2026-09-15 10:30:00',)], ['timestamp'])
    result = check_dates(df, 'telemetry').toPandas()
    assert result['__date_fail'].iloc[0] == False


def test_date_invalid_string_fails(spark):
    df = spark.createDataFrame([('not-a-date',)], ['timestamp'])
    result = check_dates(df, 'telemetry').toPandas()
    assert result['__date_fail'].iloc[0] == True


def test_date_impossible_date_fails(spark):
    df = spark.createDataFrame([('2026-15-40',)], ['timestamp'])
    result = check_dates(df, 'telemetry').toPandas()
    assert result['__date_fail'].iloc[0] == True


def test_date_null_fails(spark):
    df = spark.createDataFrame([(None,)], schema='timestamp STRING')
    result = check_dates(df, 'telemetry').toPandas()
    assert result['__date_fail'].iloc[0] == True


# ─── Schema check ─────────────────────────────────────────────
def test_schema_missing_column_detected(spark):
    df = spark.createDataFrame([('E1', 'BMW001')], ['event_id', 'vehicle_id'])
    missing = check_schema(df, 'telemetry')
    assert 'vin' in missing
    assert 'timestamp' in missing


def test_schema_all_columns_present(spark):
    schema = 'event_id STRING, vehicle_id STRING, vin STRING, timestamp STRING, battery_level DOUBLE, speed DOUBLE, temperature DOUBLE'
    df = spark.createDataFrame([], schema=schema)
    missing = check_schema(df, 'telemetry')
    assert missing == []
