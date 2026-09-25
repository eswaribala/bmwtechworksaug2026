"""Run the local BMW data lake ETL pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from bmw_data_lake.config import DEFAULT_GENERATED_DIR
from bmw_data_lake.etl import run_local_pipeline


def main() -> None:
    result = run_local_pipeline(DEFAULT_GENERATED_DIR, DEFAULT_GENERATED_DIR / "curated")
    print(result)


if __name__ == "__main__":
    main()
