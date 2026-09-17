# EV Range & Driving Efficiency Analytics

A cloud-ready analytics platform for analyzing EV driving efficiency and estimated range using Python, PySpark, Amazon S3, Athena, FastAPI and QuickSight.

## Architecture

Python ingestion/validation -> Amazon S3 raw -> AWS Glue/PySpark -> S3 curated Parquet -> Athena -> FastAPI / QuickSight.

## Analytics

- Vehicle efficiency: km/kWh
- Model efficiency
- Region efficiency
- Estimated range
- Speed vs efficiency
- Temperature vs efficiency
- Top/bottom efficiency vehicles
- Range and rolling-efficiency trends
- Charging analytics

## PySpark capabilities demonstrated

filter, select, groupBy, join, window functions, broadcast joins, repartitioning, caching, and null handling.

