"""
Test: Null detection, VIN validation, date validation, schema check
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pytest
from src.processing.validator import (
    check_nulls, check_vin, check_dates, check_schema, null_summary
)


# ─── Null detection ───────────────────────────────────────────
def test_null_detection_flags_missing_vehicle_id():
    df = pd.DataFrame({'vehicle_id': [None, 'BMW001'], 'vin': ['WBA' + 'A' * 14, 'WBA' + 'B' * 14], 'timestamp': ['2026-01-01', '2026-01-02']})
    result = check_nulls(df, 'telemetry')
    assert result['__null_fail'].iloc[0] == True
    assert result['__null_fail'].iloc[1] == False


def test_null_detection_clean_row_passes():
    df = pd.DataFrame({'vehicle_id': ['BMW001'], 'vin': ['WBA' + 'A' * 14], 'timestamp': ['2026-01-01']})
    result = check_nulls(df, 'telemetry')
    assert result['__null_fail'].iloc[0] == False


def test_null_summary_returns_correct_counts():
    df = pd.DataFrame({'vehicle_id': [None, 'BMW001', None], 'vin': ['WBA' + 'A' * 14, None, 'WBA' + 'C' * 14]})
    summary = null_summary(df, 'vehicle_master')
    vid = next(s for s in summary if s['column'] == 'vehicle_id')
    assert vid['null_count'] == 2
    assert abs(vid['null_pct'] - 66.67) < 1


# ─── VIN validation ───────────────────────────────────────────
def test_vin_valid_17_char_accepted():
    df = pd.DataFrame({'vin': ['WBA00000000000001']})
    result = check_vin(df)
    assert result['__vin_fail'].iloc[0] == False


def test_vin_invalid_short_rejected():
    df = pd.DataFrame({'vin': ['SHORT']})
    result = check_vin(df)
    assert result['__vin_fail'].iloc[0] == True


def test_vin_null_rejected():
    df = pd.DataFrame({'vin': [None]})
    result = check_vin(df)
    assert result['__vin_fail'].iloc[0] == True


def test_vin_contains_i_o_q_rejected():
    # I, O, Q are not valid in VINs
    df = pd.DataFrame({'vin': ['WBA0000000000000I']})
    result = check_vin(df)
    assert result['__vin_fail'].iloc[0] == True


# ─── Date validation ──────────────────────────────────────────
def test_date_valid_iso_passes():
    df = pd.DataFrame({'timestamp': ['2026-09-15 10:30:00']})
    result = check_dates(df, 'telemetry')
    assert result['__date_fail'].iloc[0] == False


def test_date_invalid_string_fails():
    df = pd.DataFrame({'timestamp': ['not-a-date']})
    result = check_dates(df, 'telemetry')
    assert result['__date_fail'].iloc[0] == True


def test_date_impossible_date_fails():
    df = pd.DataFrame({'timestamp': ['2026-15-40']})
    result = check_dates(df, 'telemetry')
    assert result['__date_fail'].iloc[0] == True


def test_date_null_fails():
    df = pd.DataFrame({'timestamp': [None]})
    result = check_dates(df, 'telemetry')
    assert result['__date_fail'].iloc[0] == True


# ─── Schema check ─────────────────────────────────────────────
def test_schema_missing_column_detected():
    df = pd.DataFrame({'event_id': ['E1'], 'vehicle_id': ['BMW001']})  # missing vin, timestamp etc.
    missing = check_schema(df, 'telemetry')
    assert 'vin' in missing
    assert 'timestamp' in missing


def test_schema_all_columns_present():
    df = pd.DataFrame(columns=['event_id', 'vehicle_id', 'vin', 'timestamp', 'battery_level', 'speed', 'temperature'])
    missing = check_schema(df, 'telemetry')
    assert missing == []
