# EV Range & Driving Efficiency Analytics

## Architecture
`Telemetry -> Python validation -> S3 raw -> AWS Glue/PySpark -> S3 curated Parquet -> Glue Catalog -> Athena -> FastAPI -> Streamlit`

## Configure
1. Install Python 3.11/3.12, Java 17 and AWS CLI.
2. Run `uv sync --extra dev` or `pip install -e ".[dev]"`.
3. Run `aws configure`, then `aws sts get-caller-identity`.
4. Copy `.env.example` to `.env` and set `S3_BUCKET_NAME`. Do not put AWS keys in `.env`.

## S3
Create a private bucket with Block Public Access and encryption. Upload:
```powershell
aws s3 cp data/sample/telemetry.csv s3://YOUR_BUCKET/raw/telemetry/telemetry.csv
aws s3 cp data/sample/vehicles.csv s3://YOUR_BUCKET/raw/vehicles/vehicles.csv
aws s3 cp data/sample/charging.csv s3://YOUR_BUCKET/raw/charging/charging.csv
aws s3 cp spark_jobs/ev_telemetry_job.py s3://YOUR_BUCKET/scripts/ev_telemetry_job.py
```

## Glue
The PySpark file for AWS is **`spark_jobs/ev_telemetry_job.py`**. Upload it to S3 and configure it as an AWS Glue Spark job. Pass job argument `--BUCKET YOUR_BUCKET`. Give the Glue IAM role access to the project's raw/curated/scripts paths and CloudWatch Logs.

Glue reads raw CSVs and writes Parquet to `curated/`. It demonstrates filtering, select, null handling, deduplication, join, broadcast join, groupBy, window lag, feature engineering and repartition/write concepts.

## Athena
Athena does not run PySpark. Use a Glue crawler or explicit external tables over these locations:
`curated/vehicle_efficiency/`, `model_efficiency/`, `region_efficiency/`, `range_trend/`, `driving_conditions/`.
Set Athena query results to `s3://YOUR_BUCKET/athena-results/`. Test with `SELECT * FROM vehicle_efficiency LIMIT 10;`.

## FastAPI
Start with `uv run uvicorn ev_range_analytics.api.main:app --reload`. Open `http://127.0.0.1:8000/docs`. FastAPI uses boto3 to query Athena and returns JSON.

## Streamlit
Start with `uv run streamlit run streamlit_app/app.py`. Streamlit calls FastAPI using `STREAMLIT_API_URL`; it does not directly query Athena.

## Local PySpark
Run `uv run python -m ev_range_analytics.processing.pipeline`. It reads the sample CSVs and writes local Parquet to `data/processed/`.

## Tests
Run `uv run pytest`.

## Security
Never commit `.env` or AWS secrets. Use AWS CLI profiles locally and IAM roles for Glue.

## Important distinction
**Glue executes PySpark. Athena queries the Parquet output. FastAPI queries Athena. Streamlit queries FastAPI.**
