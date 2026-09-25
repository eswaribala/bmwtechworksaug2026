from __future__ import annotations

import argparse
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish local CSV data in Athena-compatible curated layouts.")
    parser.add_argument("--input-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("build/curated"))
    parser.add_argument("--ingestion-date", default="2026-09-24")
    return parser.parse_args()


def write_parquet(
    frame: pd.DataFrame,
    path: Path,
    decimal_columns: dict[str, tuple[int, int]] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    decimal_columns = decimal_columns or {}
    for column, (_, scale) in decimal_columns.items():
        quantizer = Decimal(1).scaleb(-scale)
        frame[column] = frame[column].map(
            lambda value, quantizer=quantizer: None
            if pd.isna(value)
            else Decimal(str(value)).quantize(quantizer)
        )
    schema = pa.Schema.from_pandas(frame, preserve_index=False)
    schema = pa.schema(
        [
            pa.field(name, pa.decimal128(*decimal_columns[name]))
            if name in decimal_columns
            else field
            for name, field in zip(schema.names, schema)
        ]
    )
    table = pa.Table.from_pandas(frame, schema=schema, preserve_index=False)
    pq.write_table(table, path)


def publish(input_dir: Path, output_dir: Path, ingestion_date: str) -> None:
    dealer = pd.read_csv(input_dir / "dealer.csv")
    write_parquet(dealer, output_dir / "dealer" / "part-000.parquet")

    vehicle = pd.read_csv(input_dir / "vehicle_master.csv")
    vehicle_path = output_dir / "vehicle" / f"ingestion_date={ingestion_date}" / "vehicle_master.csv"
    vehicle_path.parent.mkdir(parents=True, exist_ok=True)
    vehicle.to_csv(vehicle_path, index=False)

    telemetry = pd.read_csv(input_dir / "telemetry.csv")
    telemetry["event_timestamp"] = pd.to_datetime(telemetry.pop("timestamp"), errors="coerce")
    telemetry["event_date"] = telemetry["event_timestamp"].dt.strftime("%Y-%m-%d")
    for event_date, partition in telemetry.groupby("event_date", dropna=False):
        write_parquet(
            partition.drop(columns=["event_date"]),
            output_dir / "telemetry" / f"event_date={event_date}" / "part-000.parquet",
        )

    sales = pd.read_csv(input_dir / "sales.csv")
    sales["sale_date"] = pd.to_datetime(sales["sale_date"], errors="coerce")
    sales["revenue"] = sales["price"] * sales["quantity"]
    sales["sale_month"] = sales["sale_date"].dt.strftime("%Y-%m")
    for sale_month, partition in sales.groupby("sale_month", dropna=False):
        write_parquet(
            partition.drop(columns=["sale_month"]),
            output_dir / "sales" / f"sale_month={sale_month}" / "part-000.parquet",
            {"price": (18, 2), "revenue": (20, 2)},
        )

    maintenance = pd.read_csv(input_dir / "maintenance.csv")
    maintenance["service_date"] = pd.to_datetime(maintenance["service_date"], errors="coerce")
    maintenance["service_cost"] = maintenance["parts_cost"].fillna(0) + maintenance["labour_cost"].fillna(0)
    maintenance["service_month"] = maintenance["service_date"].dt.strftime("%Y-%m")
    for service_month, partition in maintenance.groupby("service_month", dropna=False):
        write_parquet(
            partition.drop(columns=["service_month"]),
            output_dir / "maintenance" / f"service_month={service_month}" / "part-000.parquet",
            {
                "parts_cost": (18, 2),
                "labour_cost": (18, 2),
                "service_cost": (18, 2),
            },
        )

    warranty = pd.read_csv(input_dir / "warranty.csv")
    warranty["claim_date"] = pd.to_datetime(warranty["claim_date"], errors="coerce")
    warranty["claim_month"] = warranty["claim_date"].dt.strftime("%Y-%m")
    for claim_month, partition in warranty.groupby("claim_month", dropna=False):
        write_parquet(
            partition.drop(columns=["claim_month"]),
            output_dir / "warranty" / f"claim_month={claim_month}" / "part-000.parquet",
            {"claim_amount": (18, 2)},
        )


if __name__ == "__main__":
    args = parse_args()
    publish(args.input_dir, args.output_dir, args.ingestion_date)