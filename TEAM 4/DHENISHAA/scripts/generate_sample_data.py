"""Generate local BMW sample data for the project."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from bmw_data_lake.data_generator import generate_all_datasets


def main() -> None:
    datasets = generate_all_datasets(PROJECT_ROOT / "data" / "generated")
    for name, path in datasets.items():
        print(f"Generated {name}: {path}")


if __name__ == "__main__":
    main()
