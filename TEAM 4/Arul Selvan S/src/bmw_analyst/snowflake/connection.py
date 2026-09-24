import threading

import snowflake.connector

from config.settings import get_snowflake_config


_connection = None
_connection_lock = threading.Lock()


def _build_connection(use_database: bool = True):
    config = get_snowflake_config()

    connection_config = {
        "account": config["account"],
        "user": config["user"],
        "password": config["password"],
        "authenticator": config["authenticator"],
        "role": config["role"],
        "disable_arrow": True,
    }

    if use_database:
        connection_config.update(
            {
                "warehouse": config["warehouse"],
                "database": config["database"],
                "schema": config["schema"],
            }
        )

    return snowflake.connector.connect(**connection_config)


def get_connection(use_database: bool = True):
    """
    Return a reusable Snowflake connection.

    The first call creates the connection.
    Subsequent calls reuse the existing connection.
    """

    global _connection

    with _connection_lock:
        if _connection is None:
            _connection = _build_connection(use_database)
        else:
            try:
                if _connection.is_closed():
                    _connection = _build_connection(use_database)
            except Exception:
                # If the existing connection cannot be checked,
                # recreate it safely.
                try:
                    _connection.close()
                except Exception:
                    pass

                _connection = _build_connection(use_database)

        return _connection


def close_connection():
    """
    Explicitly close the reusable Snowflake connection.
    """

    global _connection

    with _connection_lock:
        if _connection is not None:
            try:
                _connection.close()
            finally:
                _connection = None