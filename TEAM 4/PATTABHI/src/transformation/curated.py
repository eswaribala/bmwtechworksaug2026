import pandas as pd


def enrich_sales(sales: pd.DataFrame) -> pd.DataFrame:
    result = sales.copy()
    result["revenue"] = result["price"] * result["quantity"]
    result["sale_date"] = pd.to_datetime(result["sale_date"], errors="coerce")
    return result


def enrich_maintenance(maintenance: pd.DataFrame) -> pd.DataFrame:
    result = maintenance.copy()
    result["service_cost"] = result["parts_cost"].fillna(0) + result["labour_cost"].fillna(0)
    result["service_date"] = pd.to_datetime(result["service_date"], errors="coerce")
    return result
