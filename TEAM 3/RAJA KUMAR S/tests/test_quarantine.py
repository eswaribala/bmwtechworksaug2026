"""
Tests: Quarantine mechanism
"""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.processing.quarantine import QuarantineManager


def _invalid_df(spark):
    return spark.createDataFrame(
        [
            ('E1', None, 'INVALID', 'NULL_VALUE', 'Null values in: vehicle_id'),
            ('E2', 'FAKE999', 'WBA' + 'A' * 14, 'REFERENTIAL_INTEGRITY', 'Referential integrity violation'),
        ],
        ['event_id', 'vehicle_id', 'vin', '__error_types', '__error_messages'],
    )


def test_quarantine_prepare_adds_metadata(spark):
    qm = QuarantineManager('telemetry')
    result = qm.prepare(_invalid_df(spark))
    assert 'quarantine_error_type' in result.columns
    assert 'quarantine_error_message' in result.columns
    assert 'quarantine_dataset' in result.columns
    assert 'quarantine_timestamp' in result.columns


def test_quarantine_internal_cols_removed(spark):
    qm = QuarantineManager('telemetry')
    result = qm.prepare(_invalid_df(spark))
    internal = [c for c in result.columns if c.startswith('__')]
    assert internal == []


def test_quarantine_dataset_name_correct(spark):
    qm = QuarantineManager('telemetry')
    result = qm.prepare(_invalid_df(spark)).toPandas()
    assert (result['quarantine_dataset'] == 'telemetry').all()


def test_quarantine_error_type_preserved(spark):
    qm = QuarantineManager('telemetry')
    result = qm.prepare(_invalid_df(spark)).toPandas()
    assert 'NULL_VALUE' in result['quarantine_error_type'].values


def test_quarantine_save_creates_local_file(spark):
    with tempfile.TemporaryDirectory() as tmpdir:
        qm = QuarantineManager('telemetry')
        df = qm.prepare(_invalid_df(spark))
        path = qm.save(df, tmpdir)
        assert Path(path).exists()
        saved = pd.read_csv(path)
        assert 'quarantine_error_type' in saved.columns


def test_quarantine_sample_records_returns_dicts(spark):
    qm = QuarantineManager('telemetry')
    df = qm.prepare(_invalid_df(spark))
    samples = qm.sample_records(df, n=2)
    assert isinstance(samples, list)
    assert len(samples) <= 2
    assert isinstance(samples[0], dict)
