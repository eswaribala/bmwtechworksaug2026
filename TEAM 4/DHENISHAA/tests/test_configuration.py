from bmw_data_lake.config import DEFAULT_CONFIG


def test_default_config_loads_expected_values():
    assert DEFAULT_CONFIG.project_name == "bmw-serverless-data-lake"
    assert DEFAULT_CONFIG.environment in {"dev", "test", "prod"}
    assert "us" in DEFAULT_CONFIG.aws_region
