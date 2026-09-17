"""
Tests: Duplicate detection
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.validator import check_duplicates


def test_duplicate_event_id_detected(spark):
    df = spark.createDataFrame(
        [('E1', 'BMW001'), ('E1', 'BMW001'), ('E2', 'BMW002')],
        ['event_id', 'vehicle_id'],
    )
    result = check_duplicates(df, 'telemetry').toPandas()
    # First occurrence is kept, second is flagged
    assert result['__dup_fail'].iloc[0] == False
    assert result['__dup_fail'].iloc[1] == True
    assert result['__dup_fail'].iloc[2] == False


def test_no_duplicates_all_pass(spark):
    df = spark.createDataFrame([('E1',), ('E2',), ('E3',)], ['event_id'])
    result = check_duplicates(df, 'telemetry').toPandas()
    assert result['__dup_fail'].sum() == 0


def test_duplicate_count_is_correct(spark):
    df = spark.createDataFrame([('E1',), ('E1',), ('E1',), ('E2',)], ['event_id'])
    result = check_duplicates(df, 'telemetry').toPandas()
    assert result['__dup_fail'].sum() == 2  # 2 duplicates of E1


def test_vehicle_master_duplicate_vehicle_id(spark):
    df = spark.createDataFrame([('BMW001',), ('BMW001',), ('BMW002',)], ['vehicle_id'])
    result = check_duplicates(df, 'vehicle_master').toPandas()
    assert result['__dup_fail'].iloc[1] == True


def test_empty_dataframe_no_duplicates(spark):
    df = spark.createDataFrame([], schema='event_id STRING')
    result = check_duplicates(df, 'telemetry').toPandas()
    assert result['__dup_fail'].sum() == 0
