import pandas as pd

from src.analytics.kpis import (
    average_battery,
    critical_fault_count,
    total_revenue,
    total_sales,
    total_vehicles,
    warranty_cost,
)
from src.config import Settings
from src.validation.rules import validate_vehicle_references


def test_default_bucket_name_matches_deployed_bucket():
    assert Settings().bucket_name == "bmw-executive-analytics-dashboard-pattabhi"


def test_revenue_calculation():
    assert total_revenue(pd.DataFrame({"price": [100, 250], "quantity": [2, 1]})) == 450


def test_vehicle_count():
    assert total_vehicles(pd.DataFrame({"vehicle_id": ["V1", "V1", "V2"]})) == 2


def test_battery_average():
    telemetry = pd.DataFrame({"battery_level": [80, 60]})
    assert average_battery(telemetry) == 70


def test_fault_count():
    telemetry = pd.DataFrame({"fault_code": ["P001", None, "P002"]})
    assert critical_fault_count(telemetry) == 2


def test_warranty_cost():
    assert warranty_cost(pd.DataFrame({"claim_amount": [100.0, 25.5]})) == 125.5


def test_sales_quantity():
    assert total_sales(pd.DataFrame({"quantity": [2, 3]})) == 5


def test_invalid_vehicle_reference_is_rejected():
    result = validate_vehicle_references(
        pd.DataFrame({"vehicle_id": ["V1", "UNKNOWN"]}), {"V1"}
    )
    assert len(result.valid) == 1
    assert len(result.rejected) == 1
    assert result.errors["invalid_vehicle_ids"] == 1
