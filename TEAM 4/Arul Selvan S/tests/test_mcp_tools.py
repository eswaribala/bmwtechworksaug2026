from bmw_analyst.mcp_server import tools


def test_get_vehicle_sales(monkeypatch):

    expected = [
        {
            "vehicle_id": 1001,
            "model": "BMW X1",
            "city": "Chennai",
        }
    ]

    monkeypatch.setattr(
        tools,
        "execute_query",
        lambda sql: expected,
    )

    result = tools.get_vehicle_sales()

    assert result["success"] is True
    assert result["tool"] == "get_vehicle_sales"
    assert result["data"] == expected


def test_get_warranty_cost(monkeypatch):

    expected = [
        {
            "vehicle_id": 1001,
            "model": "BMW X1",
            "warranty_cost": 45000,
        }
    ]

    monkeypatch.setattr(
        tools,
        "execute_query",
        lambda sql: expected,
    )

    result = tools.get_warranty_cost()

    assert result["success"] is True
    assert result["tool"] == "get_warranty_cost"
    assert result["data"] == expected


def test_get_fault_summary(monkeypatch):

    expected = [
        {
            "fault_type": "Engine",
            "severity": "High",
            "fault_count": 2,
        }
    ]

    monkeypatch.setattr(
        tools,
        "execute_query",
        lambda sql: expected,
    )

    result = tools.get_fault_summary()

    assert result["success"] is True
    assert result["tool"] == "get_fault_summary"
    assert result["data"] == expected


def test_get_battery_status(monkeypatch):

    expected = [
        {
            "vehicle_id": 1006,
            "model": "BMW iX",
            "battery_percentage": 35,
            "battery_status": "Critical",
        }
    ]

    monkeypatch.setattr(
        tools,
        "execute_query",
        lambda sql: expected,
    )

    result = tools.get_battery_status()

    assert result["success"] is True
    assert result["tool"] == "get_battery_status"
    assert result["data"] == expected