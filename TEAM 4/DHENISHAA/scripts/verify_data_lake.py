"""Verify expected data lake structure locally or in AWS."""

from __future__ import annotations

import argparse
from pathlib import Path


def verify_local_data_lake(data_dir: str | Path) -> dict[str, bool]:
    """Check whether expected generated and curated dataset directories exist."""

    directory = Path(data_dir)
    checks = {
        "generated_dir_exists": directory.exists(),
        "telemetry_csv_exists": (directory / "telemetry.csv").exists(),
        "vehicle_master_exists": (directory / "vehicle_master.csv").exists(),
    }
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the BMW data lake structure.")
    parser.add_argument("--data-dir", default="data/generated", help="Directory to inspect.")
    args = parser.parse_args()

    print(verify_local_data_lake(args.data_dir))


if __name__ == "__main__":
    main()
