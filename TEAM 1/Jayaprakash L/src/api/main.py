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
    return {"status": "ok"}

@app.get("/summary")
def get_summary():
    return summary()

@app.get("/vehicles/top")
def get_top(limit: int = Query(5, ge=1, le=100)):
    return top_vehicles(limit)

@app.get("/vehicles/bottom")
def get_bottom(limit: int = Query(5, ge=1, le=100)):
    return bottom_vehicles(limit)

@app.get("/models")
def get_models():
    return models()

@app.get("/regions")
def get_regions():
    return regions()

@app.get("/range-trend")
def get_range_trend():
    return range_trend()
