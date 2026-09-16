"""
Tests: Quarantine mechanism
"""
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pytest
from src.processing.quarantine import QuarantineManager


def _invalid_df():
    df = pd.DataFrame({
        'event_id': ['E1', 'E2'],
        'vehicle_id': [None, 'FAKE999'],
        'vin': ['INVALID', 'WBA' + 'A' * 14],
        '__error_types': ['NULL_VALUE', 'REFERENTIAL_INTEGRITY'],
        '__error_messages': ['Null values in: vehicle_id', 'Referential integrity violation'],
    })
    return df


def test_quarantine_prepare_adds_metadata():
    qm = QuarantineManager('telemetry')
    result = qm.prepare(_invalid_df())
    assert 'quarantine_error_type' in result.columns
    assert 'quarantine_error_message' in result.columns
    assert 'quarantine_dataset' in result.columns
    assert 'quarantine_timestamp' in result.columns


def test_quarantine_internal_cols_removed():
    qm = QuarantineManager('telemetry')
    result = qm.prepare(_invalid_df())
    internal = [c for c in result.columns if c.startswith('__')]
    assert internal == []


def test_quarantine_dataset_name_correct():
    qm = QuarantineManager('telemetry')
    result = qm.prepare(_invalid_df())
    assert (result['quarantine_dataset'] == 'telemetry').all()


def test_quarantine_error_type_preserved():
    qm = QuarantineManager('telemetry')
    result = qm.prepare(_invalid_df())
    assert 'NULL_VALUE' in result['quarantine_error_type'].values


def test_quarantine_save_creates_local_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        qm = QuarantineManager('telemetry')
        df = qm.prepare(_invalid_df())
        path = qm.save(df, tmpdir)
        assert Path(path).exists()
        saved = pd.read_csv(path)
        assert 'quarantine_error_type' in saved.columns


def test_quarantine_sample_records_returns_dicts():
    qm = QuarantineManager('telemetry')
    df = qm.prepare(_invalid_df())
    samples = qm.sample_records(df, n=2)
    assert isinstance(samples, list)
    assert len(samples) <= 2
    assert isinstance(samples[0], dict)
