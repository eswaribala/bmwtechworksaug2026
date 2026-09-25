from pathlib import Path

from bmw_data_lake.data_generator import generate_all_datasets


def test_generate_all_datasets_creates_expected_files(tmp_path):
    dataset_map = generate_all_datasets(tmp_path, seed=7)

    assert set(dataset_map.keys()) == {"vehicle_master", "telemetry", "sales", "maintenance", "warranty"}
    for path in dataset_map.values():
        assert Path(path).exists()
        assert Path(path).stat().st_size > 0
