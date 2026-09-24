# EV Battery Health Intelligence Architecture

## 1. Purpose

This project processes BMW electric vehicle telemetry, vehicle master data, and
charging-session data to produce a vehicle-level battery health dataset. Each
vehicle is classified as `Healthy`, `Watch`, or `Critical` and the result is
made available for Athena queries and a QuickSight dashboard.

The implemented architecture is:

```text
Local CSV files
      |
      | Terraform uploads raw files
      v
Amazon S3: ev-battery-health-data
  raw/telemetry/telemetry.csv
  raw/vehicle_master/vehicle_master.csv
  raw/charging_sessions/charging_sessions.csv
      |
      | PySpark reads CSV data through s3a://
      v
Local Spark ETL process
  parse and clean -> aggregate -> join -> classify
      |
      | boto3 uploads partitioned Parquet
      v
Amazon S3: curated/vehicle_health/
  battery_health_category=Healthy/part-00000.parquet
  battery_health_category=Watch/part-00000.parquet
  battery_health_category=Critical/part-00000.parquet
      |
      | Athena external table and view
      v
Athena database: ev_battery_health
  table: vehicle_health
  view: vehicle_health_dashboard
      |
      v
QuickSight SPICE dataset and dashboard
```

The current implementation runs Spark locally with `local[*]`. S3 is used for
raw input, curated output, and Athena query results; Spark itself is not
running as an AWS managed cluster.

## 2. Business Outcome

The pipeline is intended to help identify vehicles that may need monitoring or
maintenance by exposing:

- average and observed battery state of health (SoH)
- initial and latest SoH values
- absolute and percentage SoH change
- charging frequency and charging behavior
- vehicle model, age, region, capacity, and odometer context
- a health category and numeric health score

The current rule-based scores are:

| Condition | Category | Score |
|---|---|---:|
| `avg_soh >= 90` | Healthy | 100 |
| `80 <= avg_soh < 90` | Watch | 70 |
| `avg_soh < 80` | Critical | 40 |

After the initial classification, the pipeline applies two degradation checks:

- Healthy vehicles with `percent_drop > 10` are changed to `Watch`.
- Watch vehicles with `percent_drop > 15` are changed to `Critical`.

The numeric score is assigned before these two category overrides, so the
current code can produce an overridden category while retaining the original
threshold score. This is part of the current behavior and should be considered
if the scoring rules are changed later.

## 3. Repository Components

```text
architecture.md                         This implementation architecture
README.md                               Quick project instructions
pyproject.toml                          Python package and dependency metadata
quicksight_setup.md                     QuickSight connection instructions
sql/athena_setup.sql                    Athena database, table, and view SQL
terraform/                              S3 infrastructure and raw uploads
  versions.tf                           Terraform and AWS provider versions
  variables.tf                          Region, bucket, data path, and tags
  main.tf                               Bucket security and CSV upload resources
  outputs.tf                            S3 paths and uploaded object outputs
  terraform.tfvars.example              Example Terraform variables
  README.md                             Terraform usage notes
src/
  battery_health_pipeline.py            Main executable Spark pipeline
  ingestion.py                          Reusable local CSV reader helper
  transforms.py                         Reusable cleaning and aggregation helpers
  health_scoring.py                     Reusable classification/trend helpers
  dashboard_data.py                     Reusable dashboard summary helper
  athena_queries.py                     boto3 Athena query runner
  generate_battery_data.py              Synthetic CSV generator
  datas/                                Current CSV input data
```

The executable path is `src/battery_health_pipeline.py`. The modules in
`src/ingestion.py`, `src/transforms.py`, `src/health_scoring.py`, and
`src/dashboard_data.py` provide reusable building blocks, but the main
pipeline currently contains its own inline read, cleaning, aggregation, and
classification logic rather than importing those helpers.

## 4. Source Data

The current data directory is `src/datas/` and contains three CSV files.
Each file contains 200 vehicle records in the checked-in sample dataset.

### 4.1 Telemetry

`telemetry.csv` contains one telemetry record per vehicle in the current sample:

- `Vehicle_ID`
- `Timestamp`
- `SoC_Percent`
- `SoH_Percent`
- `Battery_Voltage_V`
- `Battery_Current_A`
- `Battery_Temperature_C`
- `Charging_Power_kW`
- `Vehicle_Speed_kmh`
- `Odometer_km`
- `Health_Category`

`Health_Category` is present in the generated sample data but is not used by
the production classification logic. The pipeline derives its own category
from the calculated `avg_soh` and `percent_drop` values.

### 4.2 Vehicle master

`vehicle_master.csv` provides vehicle attributes used to enrich telemetry:

- `Vehicle_ID`
- `Model`
- `Variant`
- `Model_Year`
- `Battery_Capacity_kWh`
- `Battery_Type`
- `Manufacture_Date`
- `Region`
- `Vehicle_Age_Years`
- `Odometer_km`

### 4.3 Charging sessions

`charging_sessions.csv` provides charging activity:

- `Vehicle_ID`
- `Session_Start`
- `Session_End`
- `Energy_Delivered_kWh`
- `Initial_SoC_Percent`
- `Final_SoC_Percent`
- `Charging_Duration_Min`
- `Charging_Power_kW`
- `Charging_Type`
- `Charging_Interruptions`
- `Charger_Temperature_C`
- `Environment_Temperature_C`
- `Health_Category`

## 5. Terraform and S3 Infrastructure

Terraform is in the `terraform/` directory. The defaults match the Python,
Athena, and QuickSight configuration:

- AWS region: `eu-north-1`
- bucket: `ev-battery-health-data`
- local upload directory: `../src/datas`

Terraform creates:

1. An S3 bucket with `force_destroy = false`.
2. Public access blocking on all four controls.
3. Bucket-owner-enforced object ownership.
4. AES-256 server-side encryption by default.
5. S3 versioning.
6. Three managed CSV objects.

The managed raw objects are:

```text
s3://ev-battery-health-data/raw/telemetry/telemetry.csv
s3://ev-battery-health-data/raw/vehicle_master/vehicle_master.csv
s3://ev-battery-health-data/raw/charging_sessions/charging_sessions.csv
```

Terraform discovers all `*.csv` files in the configured data directory and
creates the dataset prefix by removing the `.csv` suffix from each filename.
The curated and Athena paths are virtual S3 prefixes; they are populated by
the pipeline and Athena rather than by empty folder resources.

Typical setup:

```powershell
cd terraform
terraform init
terraform plan -out tfplan
terraform apply tfplan
```

Terraform outputs the region, bucket name, raw path, curated path, Athena
results path, and uploaded object keys.

## 6. Runtime Configuration

The pipeline reads configuration from environment variables.

| Variable | Default | Purpose |
|---|---|---|
| `AWS_REGION` | `eu-north-1` | AWS region for S3 and AWS clients |
| `READ_RAW_FROM_S3` | `true` | Read input from S3 when true |
| `WRITE_CURATED_TO_S3` | `true` | Upload curated Parquet when true |
| `RAW_S3_PATH` | `s3a://ev-battery-health-data/raw` | S3 raw base path |
| `CURATED_S3_PATH` | `s3a://ev-battery-health-data/curated/vehicle_health` | Curated output path |
| `ATHENA_DATABASE` | `ev_battery_health` | Athena database for queries |
| `ATHENA_OUTPUT_LOCATION` | `s3://ev-battery-health-data/athena-results/` | Athena query results |
| `PYSPARK_PYTHON` | environment default | Python executable for Spark workers |
| `PYSPARK_DRIVER_PYTHON` | environment default | Python executable for Spark driver |
| `SPARK_LOCAL_IP` | configured in the run instructions | Local Spark networking |

AWS credentials are resolved through the standard AWS credential chain. The
Spark S3A connector uses the AWS SDK default credentials provider, while boto3
uses the normal boto3 credential resolution process.

## 7. Executable Pipeline Flow

The main function is `build_ev_battery_health_pipeline(data_dir)` in
`src/battery_health_pipeline.py`.

### 7.1 Start Spark

The application creates a local Spark session with:

- application name `EV_Battery_Health_Intelligence`
- master `local[*]`
- driver host and bind address `127.0.0.1`
- Hadoop AWS package `org.apache.hadoop:hadoop-aws:3.5.0` when reading S3
- S3A connection timeouts of 60 seconds

If configured Python executable paths do not exist, the pipeline falls back to
`sys.executable` for Spark Python execution.

### 7.2 Resolve input paths

When `READ_RAW_FROM_S3=true`, the pipeline reads these paths:

```text
s3a://ev-battery-health-data/raw/telemetry/telemetry.csv
s3a://ev-battery-health-data/raw/vehicle_master/vehicle_master.csv
s3a://ev-battery-health-data/raw/charging_sessions/charging_sessions.csv
```

The path is formed from the filename stem, so `telemetry.csv` maps to the
`telemetry` prefix and `charging_sessions.csv` maps to the
`charging_sessions` prefix.

When `READ_RAW_FROM_S3=false`, the same filenames are read from the local
`data_dir` argument. The command-line entry point passes `src/datas`.

All three reads use a header row and Spark schema inference.

### 7.3 Clean and type the data

Telemetry processing:

- parses `Timestamp` with `yyyy-MM-dd HH:mm:ss`
- casts SoC, SoH, voltage, current, temperature, charging power, speed, and odometer to numeric types
- drops rows missing `Vehicle_ID`, `Timestamp`, or `SoH_Percent`

Vehicle master processing:

- casts model year and vehicle age to integers
- casts battery capacity and odometer to doubles
- drops rows missing `Vehicle_ID`, `Model`, or `Region`

Charging-session processing:

- parses `Session_Start` and `Session_End`
- casts energy, SoC, duration, power, and temperature fields to doubles
- casts charging interruptions to integers
- drops rows missing `Vehicle_ID`, `Session_Start`, or `Session_End`

The current executable does not implement explicit duplicate checks, range
checks, or future-timestamp checks. The null drops and type conversions above
are the validations performed in the runtime path.

### 7.4 Calculate telemetry metrics

For each `Vehicle_ID`, telemetry is aggregated into `vehicle_metrics`:

- average battery level from `SoC_Percent`
- average, minimum, and maximum `SoH_Percent`
- standard deviation of `SoH_Percent`
- telemetry record count
- first and last observed timestamps

A second ordered aggregation calculates the degradation fields:

- `initial_soh`: first SoH value after ordering by vehicle and timestamp
- `latest_soh`: last SoH value after ordering by vehicle and timestamp
- `soh_drop`: `latest_soh - initial_soh`
- `percent_drop`: `soh_drop / initial_soh * 100`

### 7.5 Calculate charging metrics

For each `Vehicle_ID`, charging sessions are aggregated into:

- `charging_frequency`: count of charging sessions
- `avg_energy_delivered_kwh`
- `avg_charging_power_kw`
- `avg_charging_duration_min`
- `charging_interruptions_count`: count of sessions with interruptions greater than zero

### 7.6 Enrich and join

The pipeline joins the telemetry metrics, vehicle master attributes, charging
metrics, and degradation metrics on `Vehicle_ID` using left joins. The result
contains the vehicle context and all calculated health features in one row per
vehicle for the current sample.

### 7.7 Classify battery health

The executable first classifies using `avg_soh`:

```text
avg_soh >= 90       -> Healthy, score 100
80 <= avg_soh < 90  -> Watch,   score 70
avg_soh < 80        -> Critical, score 40
```

It then applies the `percent_drop` overrides described in the business
outcome section. The resulting `battery_health_category` is used as the
Parquet partition column.

## 8. Curated S3 Output

When `WRITE_CURATED_TO_S3=true`, `write_parquet_to_s3` performs the following
steps:

1. Validates that `CURATED_S3_PATH` uses `s3://` or `s3a://` and contains a bucket.
2. Converts the Spark DataFrame to pandas.
3. Creates one local Parquet file per health category under a temporary directory.
4. Checks that the target bucket is accessible with `head_bucket`.
5. Lists and deletes every existing object under the curated prefix.
6. Uploads the new Parquet files with boto3.
7. Deletes the temporary local directory in a `finally` block.

The output layout is Hive-style partitioned Parquet:

```text
s3://ev-battery-health-data/curated/vehicle_health/
  battery_health_category=Healthy/part-00000.parquet
  battery_health_category=Watch/part-00000.parquet
  battery_health_category=Critical/part-00000.parquet
```

Because the implementation converts the result to pandas and writes one file
per category, it is suitable for the current small sample but is not a
large-scale distributed Parquet writer. The curated prefix is fully replaced
on each successful pipeline run.

## 9. Athena Serving Layer

Run `sql/athena_setup.sql` in Athena with the query result location set to:

```text
s3://ev-battery-health-data/athena-results/
```

The SQL creates:

- database `ev_battery_health`
- external table `ev_battery_health.vehicle_health`
- partition column `battery_health_category`
- table location `s3://ev-battery-health-data/curated/vehicle_health/`
- view `ev_battery_health.vehicle_health_dashboard`

The table schema matches the curated vehicle-level output, including SoH
metrics, vehicle attributes, charging metrics, degradation metrics, and
`health_score`. `MSCK REPAIR TABLE` discovers the category partitions after
new Parquet output is written.

The dashboard view selects the business-facing fields:

- vehicle identifier and model information
- region, age, and odometer
- average, minimum, and maximum SoH
- charging frequency, average power, and interruption count
- SoH drop and percentage drop
- battery health category and health score

`src/athena_queries.py` provides an optional boto3 helper that starts an Athena
query, polls until it succeeds or fails, and returns result rows as dictionaries.
It defaults to the same database, results path, and AWS region shown above.

## 10. QuickSight Consumption

QuickSight connects to the Athena view rather than directly to the raw CSVs.
The configured flow is:

1. Select Athena as the data source.
2. Use `AwsDataCatalog`.
3. Select database `ev_battery_health`.
4. Select view `vehicle_health_dashboard`.
5. Import the result into SPICE.
6. Build dashboard visuals for health distribution, SoH by model, regional risk,
   charging behavior, and vehicle-level risk.

After each pipeline run, refresh the Athena partitions and refresh the
QuickSight SPICE dataset so the new curated files become visible.

## 11. Local Development Mode

S3 can be bypassed for local development:

```powershell
$env:READ_RAW_FROM_S3="false"
$env:WRITE_CURATED_TO_S3="false"
python .\src\battery_health_pipeline.py
```

In this mode, the application reads from `src/datas`, returns the final Spark
DataFrame, prints sample rows, and does not upload to AWS.

For the AWS-backed path, configure Spark and AWS environment values and run:

```powershell
$env:AWS_REGION="eu-north-1"
$env:RAW_S3_PATH="s3a://ev-battery-health-data/raw"
$env:CURATED_S3_PATH="s3a://ev-battery-health-data/curated/vehicle_health"
$env:WRITE_CURATED_TO_S3="true"
python .\src\battery_health_pipeline.py
```

## 12. Data Generation

`src/generate_battery_data.py` can regenerate the sample CSV files from the
vehicle master file. It creates deterministic-looking telemetry and charging
records with three source health profiles:

- vehicle indexes 1 through 120: Healthy profile
- vehicle indexes 121 through 170: Watch profile
- vehicle indexes 171 through 200: Critical profile

Those source labels are useful for constructing the sample data, but the main
pipeline recalculates health from its measured fields and does not trust the
source `Health_Category` column.

## 13. Operational Sequence

The complete implementation sequence is:

```text
1. Generate or update src/datas/*.csv
2. terraform apply from terraform/
3. Terraform creates the bucket and uploads raw CSV objects
4. Run battery_health_pipeline.py
5. Pipeline reads the three raw S3 prefixes with Spark
6. Pipeline cleans, aggregates, joins, and classifies by vehicle
7. Pipeline replaces curated/vehicle_health/ with Parquet partitions
8. Run athena_setup.sql initially, or MSCK REPAIR TABLE after later runs
9. Query vehicle_health_dashboard in Athena
10. Refresh the QuickSight SPICE dataset
```

## 14. Current Boundaries and Risks

The current implementation has these deliberate boundaries:

- Terraform manages the bucket and raw CSV objects, but not Athena databases,
  Glue catalog objects, or QuickSight resources.
- The pipeline runs locally and uses `toPandas()`, so it should not be treated
  as a production-scale distributed writer without redesign.
- Raw CSV uploads are versioned, but the curated prefix is explicitly deleted
  and recreated for each run.
- The executable validates required fields and types but does not perform all
  data-quality checks described in the business goal, such as duplicate,
  range, or future-date detection.
- The current repository has no notebook or automated test suite; validation is
  performed through code execution, Terraform validation, and downstream
  Athena/QuickSight checks.
