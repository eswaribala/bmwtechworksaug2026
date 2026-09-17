"""
Shared pytest fixtures — provides a session-scoped local SparkSession
for all PySpark-based unit tests.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from src.utils.spark_session import get_spark, stop_spark


@pytest.fixture(scope="session")
def spark():
    session = get_spark(app_name="bmw-data-quality-tests")
    yield session
    stop_spark()
