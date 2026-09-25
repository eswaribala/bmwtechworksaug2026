import pandas as pd


def total_vehicles(vehicle_master: pd.DataFrame) -> int:
    return int(vehicle_master["vehicle_id"].nunique())


def total_sales(sales: pd.DataFrame) -> int:
    return int(sales["quantity"].sum())


def total_revenue(sales: pd.DataFrame) -> float:
    return float((sales["price"] * sales["quantity"]).sum())


def average_battery(telemetry: pd.DataFrame) -> float:
    return float(telemetry["battery_level"].mean())


def critical_fault_count(telemetry: pd.DataFrame) -> int:
    return int(telemetry["fault_code"].notna().sum())


def warranty_cost(warranty: pd.DataFrame) -> float:
    return float(warranty["claim_amount"].sum())


def service_volume(maintenance: pd.DataFrame) -> int:
    return int(maintenance["service_id"].nunique())
