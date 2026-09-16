"""
Tests: Referential Integrity
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pytest
from src.processing.validator import check_referential_integrity


def _master():
    return pd.DataFrame({'vehicle_id': ['BMW001', 'BMW002', 'BMW003']})


def test_known_vehicle_id_passes():
    telemetry = pd.DataFrame({'vehicle_id': ['BMW001', 'BMW002']})
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(), 'vehicle_id')
    assert result['__ref_fail'].sum() == 0


def test_unknown_vehicle_id_fails():
    telemetry = pd.DataFrame({'vehicle_id': ['BMW999']})
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(), 'vehicle_id')
    assert result['__ref_fail'].iloc[0] == True


def test_mixed_passes_and_fails():
    telemetry = pd.DataFrame({'vehicle_id': ['BMW001', 'FAKE001', 'BMW002']})
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(), 'vehicle_id')
    assert result['__ref_fail'].sum() == 1
    assert result['__ref_fail'].iloc[1] == True


def test_null_vehicle_id_fails():
    telemetry = pd.DataFrame({'vehicle_id': [None]})
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(), 'vehicle_id')
    assert result['__ref_fail'].iloc[0] == True


def test_all_unknown_all_fail():
    telemetry = pd.DataFrame({'vehicle_id': ['FAKE001', 'FAKE002', 'FAKE003']})
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(), 'vehicle_id')
    assert result['__ref_fail'].sum() == 3


def test_missing_fk_column_no_crash():
    telemetry = pd.DataFrame({'some_other_col': ['x', 'y']})
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(), 'vehicle_id')
    assert '__ref_fail' in result.columns
    assert result['__ref_fail'].sum() == 0
