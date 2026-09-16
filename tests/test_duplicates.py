"""
Tests: Duplicate detection
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pytest
from src.processing.validator import check_duplicates


def test_duplicate_event_id_detected():
    df = pd.DataFrame({'event_id': ['E1', 'E1', 'E2'], 'vehicle_id': ['BMW001', 'BMW001', 'BMW002']})
    result = check_duplicates(df, 'telemetry')
    # First occurrence is kept, second is flagged
    assert result['__dup_fail'].iloc[0] == False
    assert result['__dup_fail'].iloc[1] == True
    assert result['__dup_fail'].iloc[2] == False


def test_no_duplicates_all_pass():
    df = pd.DataFrame({'event_id': ['E1', 'E2', 'E3']})
    result = check_duplicates(df, 'telemetry')
    assert result['__dup_fail'].sum() == 0


def test_duplicate_count_is_correct():
    df = pd.DataFrame({'event_id': ['E1', 'E1', 'E1', 'E2']})
    result = check_duplicates(df, 'telemetry')
    assert result['__dup_fail'].sum() == 2  # 2 duplicates of E1


def test_vehicle_master_duplicate_vehicle_id():
    df = pd.DataFrame({'vehicle_id': ['BMW001', 'BMW001', 'BMW002']})
    result = check_duplicates(df, 'vehicle_master')
    assert result['__dup_fail'].iloc[1] == True


def test_empty_dataframe_no_duplicates():
    df = pd.DataFrame({'event_id': []})
    result = check_duplicates(df, 'telemetry')
    assert result['__dup_fail'].sum() == 0
