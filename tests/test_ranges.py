"""
Tests: Out-of-range validation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pytest
from src.processing.validator import check_ranges


def test_battery_150_fails():
    df = pd.DataFrame({'battery_level': [150.0], 'temperature': [20.0], 'speed': [80.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == True


def test_battery_85_passes():
    df = pd.DataFrame({'battery_level': [85.0], 'temperature': [20.0], 'speed': [80.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == False


def test_battery_negative_fails():
    df = pd.DataFrame({'battery_level': [-10.0], 'temperature': [20.0], 'speed': [80.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == True


def test_battery_zero_passes():
    df = pd.DataFrame({'battery_level': [0.0], 'temperature': [20.0], 'speed': [80.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == False


def test_battery_100_passes():
    df = pd.DataFrame({'battery_level': [100.0], 'temperature': [20.0], 'speed': [80.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == False


def test_temperature_below_min_fails():
    df = pd.DataFrame({'battery_level': [50.0], 'temperature': [-50.0], 'speed': [80.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == True


def test_temperature_above_max_fails():
    df = pd.DataFrame({'battery_level': [50.0], 'temperature': [130.0], 'speed': [80.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == True


def test_speed_over_300_fails():
    df = pd.DataFrame({'battery_level': [50.0], 'temperature': [20.0], 'speed': [350.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == True


def test_all_in_range_passes():
    df = pd.DataFrame({'battery_level': [50.0], 'temperature': [20.0], 'speed': [120.0]})
    result = check_ranges(df)
    assert result['__range_fail'].iloc[0] == False


def test_range_cols_identifies_column():
    df = pd.DataFrame({'battery_level': [150.0], 'temperature': [20.0], 'speed': [80.0]})
    result = check_ranges(df)
    assert 'battery_level' in result['__range_cols'].iloc[0]
