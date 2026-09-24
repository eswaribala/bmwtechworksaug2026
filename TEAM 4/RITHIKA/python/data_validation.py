import pandas as pd

from python.logger import get_logger

logger = get_logger(__name__)


def validate_telemetry(df: pd.DataFrame) -> bool:
    required_columns = {
        "vehicle_id",
        "model",
        "battery_level",
        "temperature",
        "speed",
        "region",
        "event_timestamp",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing telemetry columns: {sorted(missing_columns)}"
        )

    if df["vehicle_id"].isna().any():
        raise ValueError("vehicle_id cannot be NULL")

    if (~df["battery_level"].between(0, 100)).any():
        raise ValueError("battery_level must be between 0 and 100")

    if (df["speed"] < 0).any():
        raise ValueError("speed cannot be negative")

    logger.info("Telemetry validation passed")

    return True


def validate_sales(df: pd.DataFrame) -> bool:
    required_columns = {
        "sales_id",
        "customer_id",
        "vehicle_id",
        "dealer_id",
        "purchase_date",
        "sale_price",
        "quantity",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing sales columns: {sorted(missing_columns)}"
        )

    if df["sales_id"].isna().any():
        raise ValueError("sales_id cannot be NULL")

    if (df["sale_price"] < 0).any():
        raise ValueError("sale_price cannot be negative")

    if (df["quantity"] <= 0).any():
        raise ValueError("quantity must be greater than zero")

    logger.info("Sales validation passed")

    return True