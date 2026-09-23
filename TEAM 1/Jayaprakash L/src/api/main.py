"""FastAPI application exposing EV analytics endpoints.

The API is intentionally thin: route handlers validate request parameters
and delegate data retrieval to :mod:`src.api.queries`.
"""

from fastapi import FastAPI, Query
from .queries import (
    summary, top_vehicles, bottom_vehicles,
    models, regions, range_trend
)

app = FastAPI(
    title="EV Range & Driving Efficiency API",
    version="1.0.0"
)

@app.get("/health")
def health():
    """Return a lightweight health status for service checks."""
    return {"status": "ok"}

@app.get("/summary")
def get_summary():
    """Return summary analytics."""
    return summary()

@app.get("/vehicles/top")
def get_top(limit: int = Query(5, ge=1, le=100)):
    """Return the requested number of top-efficiency vehicles."""
    return top_vehicles(limit)

@app.get("/vehicles/bottom")
def get_bottom(limit: int = Query(5, ge=1, le=100)):
    """Return the requested number of bottom-efficiency vehicles."""
    return bottom_vehicles(limit)

@app.get("/models")
def get_models():
    """Return model efficiency analytics."""
    return models()

@app.get("/regions")
def get_regions():
    """Return region efficiency analytics."""
    return regions()

@app.get("/range-trend")
def get_range_trend():
    """Return the daily range trend."""
    return range_trend()
