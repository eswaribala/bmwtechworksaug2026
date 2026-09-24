import os

import pytest


pytestmark = pytest.mark.integration


def test_snowflake_connection():
    required = {
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_AUTHENTICATOR",
        "SNOWFLAKE_ROLE",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
    }
    if not required.issubset(os.environ):
        pytest.skip("Snowflake integration credentials are not configured")

    from bmw_analyst.snowflake.connection import get_connection

    connection = get_connection(use_database=False)


    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT CURRENT_USER(), CURRENT_ACCOUNT()"
        )

        result = cursor.fetchone()

        assert result is not None

    finally:
        connection.close()