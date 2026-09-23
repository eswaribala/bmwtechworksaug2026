# EV Range & Driving Efficiency Analytics

End-to-end project:

CSV → Python validation → S3 raw → PySpark → S3 curated Parquet → Glue Catalog → Athena → FastAPI → Streamlit.

## Main outputs
- Efficiency by vehicle
- Efficiency by model
- Efficiency by region
- Range trend
- Top 5 efficiency vehicles
- Bottom 5 efficiency vehicles

## Efficiency formula

For each vehicle:

`battery_consumed = previous_battery_percent - current_battery_percent`

For positive battery consumption:

`event_efficiency = distance_km / battery_consumed`

Vehicle efficiency:

`overall_efficiency = total_distance_km / total_battery_consumed`

## Local setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
python scripts/run_local_pipeline.py
uvicorn src.api.main:app --reload
streamlit run src/dashboard/app.py
```

The generated dataset contains 50 vehicles × 12 telemetry records.

## API
- GET /health
- GET /summary
- GET /vehicles/top?limit=5
- GET /vehicles/bottom?limit=5
- GET /models
- GET /regions
- GET /range-trend

## AWS architecture

S3 raw → Glue/PySpark → S3 curated Parquet → Glue Catalog → Athena → FastAPI → Streamlit.

The `scripts/glue_job.py` file is the AWS Glue version of the Spark transformation.
