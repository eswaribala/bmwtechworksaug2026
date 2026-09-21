from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="BMW Enterprise Batch ETL API",
    description="API for accessing BMW batch ETL analytics and processed data.",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATA LOADING
# ============================================================

def load_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Load a processed Parquet dataset from the ETL output directory.

    Supports both:
    1. A single Parquet file:
       data/processed/<dataset>/part-00000.parquet

    2. A partitioned Parquet dataset:
       data/processed/<dataset>/region=East/*.parquet
       data/processed/<dataset>/region=North/*.parquet
       etc.
    """

    dataset_dir = PROCESSED_DIR / dataset_name

    if not dataset_dir.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Processed dataset not found: {dataset_name}",
        )

    try:
        # ----------------------------------------------------
        # Case 1: Single Parquet file
        # ----------------------------------------------------

        single_file = dataset_dir / "part-00000.parquet"

        if single_file.exists():
            return pd.read_parquet(single_file)

        # ----------------------------------------------------
        # Case 2: Partitioned Parquet dataset
        # ----------------------------------------------------

        parquet_files = list(dataset_dir.rglob("*.parquet"))

        if parquet_files:
            return pd.read_parquet(dataset_dir)

        # ----------------------------------------------------
        # No Parquet files found
        # ----------------------------------------------------

        raise HTTPException(
            status_code=404,
            detail=f"No Parquet files found for dataset: {dataset_name}",
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to read dataset '{dataset_name}': {str(exc)}",
        )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    """
    Root endpoint for the BMW Enterprise Batch ETL API.
    """

    return {
        "message": "BMW Enterprise Batch ETL API is running",
        "status": "success",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """

    return {
        "status": "healthy",
    }


# ============================================================
# KPI 1 — SUMMARY
# ============================================================

@app.get("/api/kpis/summary")
def get_summary():
    """
    Return high-level BMW sales and maintenance KPIs.
    """

    sales = load_dataset("sales")
    maintenance = load_dataset("maintenance")

    return {
        "total_revenue": round(
            float(sales["revenue"].sum()),
            2,
        ),
        "total_vehicles_sold": int(
            sales["quantity"].sum()
        ),
        "total_sales_records": int(
            len(sales)
        ),
        "total_maintenance_records": int(
            len(maintenance)
        ),
        "total_maintenance_cost": round(
            float(maintenance["total_service_cost"].sum()),
            2,
        ),
    }


# ============================================================
# KPI 2 — SALES BY MODEL
# ============================================================

@app.get("/api/kpis/models")
def get_model_kpis():
    """
    Return sales and revenue grouped by BMW model.
    """

    sales = load_dataset("sales")

    result = (
        sales.groupby(
            "model",
            as_index=False,
        )
        .agg(
            vehicles_sold=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
        )
        .sort_values(
            "total_revenue",
            ascending=False,
        )
    )

    result["total_revenue"] = (
        result["total_revenue"].round(2)
    )

    return result.to_dict(
        orient="records"
    )


# ============================================================
# KPI 3 — SALES BY REGION
# ============================================================

@app.get("/api/kpis/regions")
def get_region_kpis():
    """
    Return sales and revenue grouped by region.
    """

    sales = load_dataset("sales")

    result = (
        sales.groupby(
            "region",
            dropna=False,
            as_index=False,
        )
        .agg(
            vehicles_sold=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
        )
        .sort_values(
            "total_revenue",
            ascending=False,
        )
    )

    result["region"] = (
        result["region"].fillna("Missing")
    )

    result["total_revenue"] = (
        result["total_revenue"].round(2)
    )

    return result.to_dict(
        orient="records"
    )


# ============================================================
# KPI 4 — MAINTENANCE BY SERVICE TYPE
# ============================================================

@app.get("/api/kpis/maintenance")
def get_maintenance_kpis():
    """
    Return maintenance cost grouped by service type.
    """

    maintenance = load_dataset("maintenance")

    result = (
        maintenance.groupby(
            "service_type",
            as_index=False,
        )
        .agg(
            service_count=("service_id", "count"),
            total_maintenance_cost=(
                "total_service_cost",
                "sum",
            ),
        )
        .sort_values(
            "total_maintenance_cost",
            ascending=False,
        )
    )

    result["total_maintenance_cost"] = (
        result["total_maintenance_cost"].round(2)
    )

    return result.to_dict(
        orient="records"
    )


# ============================================================
# KPI 5 — TOP 10 DEALERS BY REVENUE
# ============================================================

@app.get("/api/kpis/dealers")
def get_dealer_kpis():
    """
    Return the top 10 dealers by revenue.
    """

    sales = load_dataset("sales")
    dealers = load_dataset("dealer")

    # The sales dataset also contains a "region" column.
    # Remove it before joining so that the dealer's region
    # remains available as the single "region" column.

    sales_for_join = sales.drop(
        columns=["region"]
    )

    # Join sales with dealer information.

    result = sales_for_join.merge(
        dealers[
            [
                "dealer_id",
                "dealer_name",
                "city",
                "region",
            ]
        ],
        on="dealer_id",
        how="inner",
    )

    # Aggregate dealer-level sales.

    result = (
        result.groupby(
            [
                "dealer_id",
                "dealer_name",
                "city",
                "region",
            ],
            as_index=False,
        )
        .agg(
            vehicles_sold=("quantity", "sum"),
            total_revenue=("revenue", "sum"),
        )
        .sort_values(
            "total_revenue",
            ascending=False,
        )
        .head(10)
    )

    # Round revenue to two decimal places.

    result["total_revenue"] = (
        result["total_revenue"].round(2)
    )

    return result.to_dict(
        orient="records"
    )