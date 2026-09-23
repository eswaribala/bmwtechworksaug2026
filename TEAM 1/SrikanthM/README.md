# EV Battery Health Intelligence

This project analyzes EV battery degradation using vehicle telemetry, vehicle master data, and charging session records.

## Objective
Identify vehicles whose batteries are degrading abnormally and classify them as:
- Healthy
- Watch
- Critical

## Data Sources
- telemetry.csv
- vehicle_master.csv
- charging_sessions.csv

## Tech Stack
- Python
- PySpark
- S3 / object storage
- Athena / AWS Glue Catalog
- QuickSight

## Project Structure
```text
capstone-project/
├── telemetry.csv
├── vehicle_master.csv
├── charging_sessions.csv
├── pyproject.toml
├── architecture.md
├── README.md
│   ├── ingestion.py
│   ├── transforms.py
│   ├── health_scoring.py
│   └── dashboard_data.py
├── sql/
│   └── athena_setup.sql
└── quicksight_setup.md
```

## S3 to Athena to QuickSight

The pipeline reads raw CSV files directly from S3 and writes the classified
vehicle health result as partitioned Parquet to S3:

```text
s3://ev-battery-health-data/raw/
    -> PySpark
    -> s3://ev-battery-health-data/curated/vehicle_health/
    -> Athena/Glue Catalog table
    -> QuickSight dashboard
```

Run the pipeline from PowerShell:

```powershell
$env:HADOOP_HOME="C:\Users\SrikanthM\Downloads\hadoop-win-utils"
$env:hadoop_home_dir=$env:HADOOP_HOME
$env:PATH="$env:HADOOP_HOME\bin;$env:PATH"
$env:AWS_REGION="eu-north-1"
$env:RAW_S3_PATH="s3a://ev-battery-health-data/raw"
$env:CURATED_S3_PATH="s3a://ev-battery-health-data/curated/vehicle_health"
$env:WRITE_CURATED_TO_S3="true"
$env:SPARK_LOCAL_IP="127.0.0.1"
$env:PYSPARK_PYTHON=(Get-Command python).Source
$env:PYSPARK_DRIVER_PYTHON=(Get-Command python).Source
python .\src\battery_health_pipeline.py
```

Execute [sql/athena_setup.sql](sql/athena_setup.sql) in the Athena Query Editor.
It creates the Glue Catalog table, repairs the S3 partitions, and creates the
dashboard view. The Python helper [src/athena_queries.py](src/athena_queries.py)
can run Athena queries through boto3.

Finally follow [quicksight_setup.md](quicksight_setup.md) to connect QuickSight
to the Athena dashboard view.

## Local Development

To run without S3, set both flags to false:

```powershell
$env:READ_RAW_FROM_S3="false"
$env:WRITE_CURATED_TO_S3="false"
python .\src\battery_health_pipeline.py
```

## Documentation

Install the documentation dependencies and build the Sphinx site:

```powershell
python -m pip install -e ".[docs]"
python -m sphinx -b html -W docs docs/_build/html
```

Open `docs/_build/html/index.html` after the build. The documentation covers
the architecture, calculations, configuration, operations, and generated
Python API reference.

## Next Steps
1. Load data with PySpark
2. Clean and validate schema
3. Join telemetry with vehicle master data
4. Compute battery health metrics
5. Classify vehicles using thresholds
6. Publish curated Parquet to S3
7. Refresh Athena partitions
8. Refresh QuickSight


output url:
https://eu-north-1.quicksight.aws.amazon.com/sn/account/tamizh-sk/accounts/532404260630/dashboards/f35efd04-f1ca-453b-9a3c-805ea77a0564