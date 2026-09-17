"""
Tests: Referential Integrity
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.validator import check_referential_integrity


def _master(spark):
    return spark.createDataFrame([('BMW001',), ('BMW002',), ('BMW003',)], ['vehicle_id'])


def test_known_vehicle_id_passes(spark):
    telemetry = spark.createDataFrame([('BMW001',), ('BMW002',)], ['vehicle_id'])
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(spark), 'vehicle_id').toPandas()
    assert result['__ref_fail'].sum() == 0


def test_unknown_vehicle_id_fails(spark):
    telemetry = spark.createDataFrame([('BMW999',)], ['vehicle_id'])
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(spark), 'vehicle_id').toPandas()
    assert result['__ref_fail'].iloc[0] == True


def test_mixed_passes_and_fails(spark):
    telemetry = spark.createDataFrame([('BMW001',), ('FAKE001',), ('BMW002',)], ['vehicle_id'])
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(spark), 'vehicle_id').toPandas()
    assert result['__ref_fail'].sum() == 1
    assert result['__ref_fail'].iloc[1] == True


def test_null_vehicle_id_fails(spark):
    telemetry = spark.createDataFrame([(None,)], schema='vehicle_id STRING')
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(spark), 'vehicle_id').toPandas()
    assert result['__ref_fail'].iloc[0] == True


def test_all_unknown_all_fail(spark):
    telemetry = spark.createDataFrame([('FAKE001',), ('FAKE002',), ('FAKE003',)], ['vehicle_id'])
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(spark), 'vehicle_id').toPandas()
    assert result['__ref_fail'].sum() == 3


def test_missing_fk_column_no_crash(spark):
    telemetry = spark.createDataFrame([('x',), ('y',)], ['some_other_col'])
    result = check_referential_integrity(telemetry, 'vehicle_id', _master(spark), 'vehicle_id').toPandas()
    assert '__ref_fail' in result.columns
    assert result['__ref_fail'].sum() == 0
