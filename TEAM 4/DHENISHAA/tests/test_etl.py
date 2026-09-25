from pathlib import Path

from bmw_data_lake.data_generator import generate_telemetry
from bmw_data_lake.etl import run_local_telemetry_etl


def test_run_local_telemetry_etl_writes_partitioned_output(tmp_path):
    telemetry_path = generate_telemetry(tmp_path, seed=9, rows=100)
    output_dir = tmp_path / "curated"

    files, summary = run_local_telemetry_etl(telemetry_path, output_dir=output_dir)

    assert files
    assert summary["output_files"] == len(files)
    assert any("year=" in str(path) for path in files)

    rejected_csv = tmp_path / "curated" / "../rejected" / "telemetry_rejected.csv"
    assert Path(rejected_csv).exists() or Path(output_dir.parent / "rejected" / "telemetry_rejected.csv").exists()
