import re
import time
from typing import Any

from snowflake.connector.errors import InterfaceError, OperationalError

from config.settings import (
    MAX_QUERY_ROWS,
    QUERY_RETRY_ATTEMPTS,
    QUERY_RETRY_BACKOFF_SECONDS,
    QUERY_TIMEOUT_SECONDS,
)

from bmw_analyst.security.logging_config import logger

from .connection import get_connection, close_connection


def apply_query_limit(sql: str) -> str:
    """
    Ensure the SQL query has a safe maximum row limit.
    """

    sql = sql.strip().rstrip(";").strip()

    if re.search(r"\bLIMIT\s+\d+\b", sql, re.IGNORECASE):
        return sql

    return f"{sql}\nLIMIT {MAX_QUERY_ROWS}"


def execute_query(
    sql: str,
    params: tuple[Any, ...] | None = None,
) -> list[dict[str, Any]]:

    for attempt in range(1, QUERY_RETRY_ATTEMPTS + 1):
        try:
            return _execute_query_once(sql, params)

        except (
            InterfaceError,
            OperationalError,
            TimeoutError,
            ConnectionError,
        ) as exc:

            if attempt == QUERY_RETRY_ATTEMPTS:
                logger.exception(
                    "Snowflake query failed after retries"
                )
                raise

            # Recreate the connection before retrying.
            try:
                close_connection()
            except Exception:
                pass

            delay = QUERY_RETRY_BACKOFF_SECONDS * (
                2 ** (attempt - 1)
            )

            logger.warning(
                "Transient Snowflake failure; "
                "retrying attempt=%s next_attempt=%s "
                "delay=%s error=%s",
                attempt,
                attempt + 1,
                delay,
                str(exc),
            )

            time.sleep(delay)


def _execute_query_once(
    sql: str,
    params: tuple[Any, ...] | None,
) -> list[dict[str, Any]]:

    logger.info("Snowflake query execution started")

    connection = get_connection()

    cursor = None

    try:
        cursor = connection.cursor()

        safe_sql = apply_query_limit(sql)

        logger.info(
            "Executing Snowflake query "
            "with max_rows=%s timeout=%s",
            MAX_QUERY_ROWS,
            QUERY_TIMEOUT_SECONDS,
        )

        cursor.execute(
            safe_sql,
            params,
            timeout=QUERY_TIMEOUT_SECONDS,
        )

        columns = [
            column[0]
            for column in cursor.description
        ]

        rows = cursor.fetchmany(MAX_QUERY_ROWS)

        result = [
            dict(zip(columns, row))
            for row in rows
        ]

        logger.info(
            "Snowflake query completed successfully "
            "rows_returned=%s",
            len(result),
        )

        return result

    except Exception:
        logger.exception(
            "Snowflake query execution failed"
        )
        raise

    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass

        # IMPORTANT:
        # Do NOT close the Snowflake connection here.
        #
        # It is intentionally kept alive and reused
        # by subsequent queries.