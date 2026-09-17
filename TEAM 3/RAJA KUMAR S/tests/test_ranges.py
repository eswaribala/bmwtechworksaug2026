"""
Tests: Out-of-range validation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.validator import check_ranges

COLS = ['battery_level', 'temperature', 'speed']


def test_battery_150_fails(spark):
    df = spark.createDataFrame([(150.0, 20.0, 80.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == True


def test_battery_85_passes(spark):
    df = spark.createDataFrame([(85.0, 20.0, 80.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == False


def test_battery_negative_fails(spark):
    df = spark.createDataFrame([(-10.0, 20.0, 80.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == True


def test_battery_zero_passes(spark):
    df = spark.createDataFrame([(0.0, 20.0, 80.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == False


def test_battery_100_passes(spark):
    df = spark.createDataFrame([(100.0, 20.0, 80.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == False


def test_temperature_below_min_fails(spark):
    df = spark.createDataFrame([(50.0, -50.0, 80.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == True


def test_temperature_above_max_fails(spark):
    df = spark.createDataFrame([(50.0, 130.0, 80.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == True


def test_speed_over_300_fails(spark):
    df = spark.createDataFrame([(50.0, 20.0, 350.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == True


def test_all_in_range_passes(spark):
    df = spark.createDataFrame([(50.0, 20.0, 120.0)], COLS)
    result = check_ranges(df).toPandas()
    assert result['__range_fail'].iloc[0] == False


def test_range_cols_identifies_column(spark):
    df = spark.createDataFrame([(150.0, 20.0, 80.0)], COLS)
    result = check_ranges(df).toPandas()
    assert 'battery_level' in result['__range_cols'].iloc[0]
