from pathlib import Path
import csv

from bmw_analyst.snowflake.connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "sample"

DATABASE = "BMW_ANALYTICS"
SCHEMA = "BMW_DATA"


TABLES = {
    "battery.csv": {
        "table": "BMW_BATTERY",
        "columns": [
            "VEHICLE_ID",
            "MODEL",
            "CITY",
            "BATTERY_DATE",
            "BATTERY_PERCENTAGE",
            "BATTERY_STATUS",
        ],
    },
    "faults.csv": {
        "table": "BMW_FAULTS",
        "columns": [
            "VEHICLE_ID",
            "MODEL",
            "CITY",
            "FAULT_DATE",
            "FAULT_TYPE",
            "SEVERITY",
        ],
    },
    "vehicle_sales.csv": {
        "table": "BMW_VEHICLE_SALES",
        "columns": [
            "VEHICLE_ID",
            "MODEL",
            "CITY",
            "SALE_DATE",
            "SALES_AMOUNT",
            "QUANTITY",
        ],
    },
    "warranty.csv": {
        "table": "BMW_WARRANTY",
        "columns": [
            "VEHICLE_ID",
            "MODEL",
            "CITY",
            "WARRANTY_DATE",
            "FAULT_TYPE",
            "WARRANTY_COST",
        ],
    },
}


def load_csv(cursor, filename, config):
    csv_path = DATA_DIR / filename
    table = config["table"]
    expected_columns = config["columns"]

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    print(f"\nLoading: {csv_path}")
    print(f"Target : {DATABASE}.{SCHEMA}.{table}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)

        header = next(reader, None)

        if header is None:
            raise ValueError(f"{filename} is empty")

        header = [column.strip().upper() for column in header]

        if header != expected_columns:
            raise ValueError(
                f"Column mismatch in {filename}\n"
                f"Expected: {expected_columns}\n"
                f"Actual:   {header}"
            )

        rows = list(reader)

    if not rows:
        raise ValueError(f"{filename} contains no data rows")

    for row_number, row in enumerate(rows, start=2):
        if len(row) != len(expected_columns):
            raise ValueError(
                f"{filename}: row {row_number} has "
                f"{len(row)} columns; expected {len(expected_columns)}"
            )

    qualified_table = f"{DATABASE}.{SCHEMA}.{table}"

    # Replace existing contents.
    cursor.execute(f"TRUNCATE TABLE {qualified_table}")

    placeholders = ", ".join(["%s"] * len(expected_columns))
    column_sql = ", ".join(expected_columns)

    insert_sql = (
        f"INSERT INTO {qualified_table} "
        f"({column_sql}) "
        f"VALUES ({placeholders})"
    )

    cursor.executemany(insert_sql, rows)

    cursor.execute(f"SELECT COUNT(*) FROM {qualified_table}")
    count = cursor.fetchone()[0]

    print(f"Loaded rows: {len(rows)}")
    print(f"Snowflake count: {count}")

    if count != len(rows):
        raise RuntimeError(
            f"Row count mismatch for {table}: "
            f"CSV={len(rows)}, Snowflake={count}"
        )


def main():
    connection = get_connection(use_database=False)

    try:
        cursor = connection.cursor()

        cursor.execute(f"USE DATABASE {DATABASE}")
        cursor.execute(f"USE SCHEMA {SCHEMA}")

        try:
            for filename, config in TABLES.items():
                load_csv(cursor, filename, config)

            connection.commit()

            print("\n========================================")
            print("CSV LOAD COMPLETED SUCCESSFULLY")
            print("========================================")

        except Exception:
            connection.rollback()
            print("\nLOAD FAILED - ROLLED BACK")
            raise

        finally:
            cursor.close()

    finally:
        connection.close()


if __name__ == "__main__":
    main()