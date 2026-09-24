import os
import json
from pathlib import Path

import boto3
from dotenv import load_dotenv


# -------------------------------------------------
# Project Paths
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# -------------------------------------------------
# AWS Configuration
# -------------------------------------------------

AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-south-1",
)


# -------------------------------------------------
# Optional AWS Secrets Manager
# -------------------------------------------------

def _load_secret_values() -> dict[str, str]:
    """
    Load optional application secrets from AWS Secrets Manager.

    This is retained for compatibility with the existing project.
    Ollama itself does not require AWS.
    """

    secret_name = os.getenv(
        "AWS_SECRETS_MANAGER_SECRET_NAME"
    )

    if not secret_name:
        return {}

    response = boto3.client(
        "secretsmanager",
        region_name=AWS_REGION,
    ).get_secret_value(
        SecretId=secret_name
    )

    secret_string = response.get(
        "SecretString",
        "{}",
    )

    values = json.loads(secret_string)

    if not isinstance(values, dict):
        raise RuntimeError(
            "Secrets Manager secret must contain a JSON object."
        )

    return {
        str(key): str(value)
        for key, value in values.items()
    }


_SECRET_VALUES = _load_secret_values()


# -------------------------------------------------
# Environment Helpers
# -------------------------------------------------

def get_required_env(name: str) -> str:
    """
    Read a required environment variable.

    Environment variables take priority over
    Secrets Manager values.
    """

    value = (
        os.getenv(name)
        or _SECRET_VALUES.get(name)
    )

    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' "
            f"is missing from {ENV_FILE}"
        )

    return value


# -------------------------------------------------
# Snowflake Configuration
# -------------------------------------------------

SNOWFLAKE_ACCOUNT = get_required_env(
    "SNOWFLAKE_ACCOUNT"
)

SNOWFLAKE_USER = get_required_env(
    "SNOWFLAKE_USER"
)

SNOWFLAKE_PASSWORD = get_required_env(
    "SNOWFLAKE_PASSWORD"
)

SNOWFLAKE_AUTHENTICATOR = get_required_env(
    "SNOWFLAKE_AUTHENTICATOR"
)

SNOWFLAKE_ROLE = get_required_env(
    "SNOWFLAKE_ROLE"
)

SNOWFLAKE_WAREHOUSE = get_required_env(
    "SNOWFLAKE_WAREHOUSE"
)

SNOWFLAKE_DATABASE = get_required_env(
    "SNOWFLAKE_DATABASE"
)

SNOWFLAKE_SCHEMA = get_required_env(
    "SNOWFLAKE_SCHEMA"
)


def get_snowflake_config() -> dict:
    """
    Return Snowflake connection configuration.
    """

    return {
        "account": SNOWFLAKE_ACCOUNT,
        "user": SNOWFLAKE_USER,
        "password": SNOWFLAKE_PASSWORD,
        "authenticator": SNOWFLAKE_AUTHENTICATOR,
        "role": SNOWFLAKE_ROLE,
        "warehouse": SNOWFLAKE_WAREHOUSE,
        "database": SNOWFLAKE_DATABASE,
        "schema": SNOWFLAKE_SCHEMA,
    }


# -------------------------------------------------
# Ollama / Qwen Configuration
# -------------------------------------------------

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:7b",
)


# -------------------------------------------------
# API Configuration
# -------------------------------------------------

API_HOST = get_required_env(
    "API_HOST"
)

API_PORT = int(
    get_required_env("API_PORT")
)


# -------------------------------------------------
# Streamlit Configuration
# -------------------------------------------------

STREAMLIT_HOST = get_required_env(
    "STREAMLIT_HOST"
)

STREAMLIT_PORT = int(
    get_required_env("STREAMLIT_PORT")
)


# Optional for local development.
# Production deployments should set it.

API_KEY = (
    os.getenv("API_KEY")
    or _SECRET_VALUES.get("API_KEY")
)


# -------------------------------------------------
# Application Configuration
# -------------------------------------------------

MCP_SERVER_NAME = get_required_env(
    "MCP_SERVER_NAME"
)

APP_NAME = get_required_env(
    "APP_NAME"
)

LOG_LEVEL = get_required_env(
    "LOG_LEVEL"
)


# -------------------------------------------------
# Approved Database Tables
# -------------------------------------------------

APPROVED_TABLES = {
    "BMW_VEHICLE_SALES",
    "BMW_WARRANTY",
    "BMW_FAULTS",
    "BMW_BATTERY",
}


# -------------------------------------------------
# Approved MCP Tools
# -------------------------------------------------

APPROVED_MCP_TOOLS = {
    "get_vehicle_sales",
    "get_warranty_cost",
    "get_fault_summary",
    "get_battery_status",
    "execute_approved_query",
}


# -------------------------------------------------
# SQL Security
# -------------------------------------------------

ALLOWED_SQL_COMMAND = "SELECT"

BLOCKED_SQL_COMMANDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "MERGE",
    "GRANT",
    "REVOKE",
}


# -------------------------------------------------
# Query Resource Protection
# -------------------------------------------------

MAX_QUERY_ROWS = 1000

QUERY_TIMEOUT_SECONDS = 30

QUERY_RETRY_ATTEMPTS = 3

QUERY_RETRY_BACKOFF_SECONDS = 0.5

MAX_QUESTION_LENGTH = 1000