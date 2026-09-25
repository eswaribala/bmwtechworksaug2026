from pathlib import Path

from bmw_data_lake.partitioning import build_partition_directory, telemetry_partition_path


def test_telemetry_partition_path_formats_expected_layout():
    assert telemetry_partition_path(2024, 2) == "year=2024/month=02"
    assert telemetry_partition_path(2024, 2, region="Europe") == "region=Europe/year=2024/month=02"


def test_build_partition_directory_uses_base_and_partition_path(tmp_path):
    directory = build_partition_directory(tmp_path, 2024, 7, region="North America")

    assert directory.parts[-3:] == ("region=North America", "year=2024", "month=07")
    assert Path(directory).name == "month=07"
