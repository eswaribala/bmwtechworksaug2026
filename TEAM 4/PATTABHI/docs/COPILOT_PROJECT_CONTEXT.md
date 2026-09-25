# BMW Executive Analytics Dashboard - Copilot Project Context

Use this document as the working context for all future implementation, debugging, review, and planning in this repository.

## 1. Project Goal

Build a governed BMW executive analytics platform that gives leadership one trusted view of commercial performance and vehicle health.

The platform must ingest six CSV source domains, validate and curate the data, expose Athena tables and KPI views, and provide a QuickSight executive dashboard with regional row-level security.

The MVP is batch-oriented and refreshes daily. Predictive maintenance, real-time streaming, customer PII enrichment, and Snowflake are out of scope unless explicitly requested as post-MVP extensions.

## 2. Users and Business Outcomes

- Executives need headline KPIs, trends, regional comparisons, and freshness information.
- Regional managers need drill-down from BMW to region, dealer, and model, restricted to their own region.
- Data and platform owners need visibility into validation failures, processing failures, freshness, and operational health.

## 3. Repository Map

```text
generate_data.py                 Deterministic sample-data generator
README.md                        Setup and AWS overview
requirements.txt                 Python dependencies
data/                            Local sample CSV files
docs/                            Product, architecture, operations, and design documents
sql/001_create_database.sql      Athena database and external table DDL
sql/002_kpi_queries.sql          KPI, trend, regional, model, and dealer queries
sql/003_curated_views.sql        Athena executive KPI view
src/config.py                    Environment-based settings
src/ingestion/csv_loader.py      Local CSV loading helper
src/validation/rules.py           Validation result model and validation rules
src/transformation/curated.py    Derived revenue, service cost, and date fields
src/analytics/kpis.py            Python KPI calculations
src/utils/logging_config.py      Application logging setup
tests/test_kpis.py               KPI and validation tests
terraform/main.tf                S3 bucket, security controls, and folder markers
terraform/variables.tf           AWS region and bucket name variables
.github/workflows/ci.yml         Lint, test, package, and SQL deployment workflow
```

## 4. AWS Environment and S3 Layout

- Region: `eu-central-1`
- Current bucket: `bmw-executive-analytics-dashboard-pattabhi`
- Terraform directory: `terraform/`
- The new bucket was applied with isolated state at `terraform/pattabhi.tfstate`; the default `terraform.tfstate` still belongs to the previous bucket and must not be used to manage both buckets interchangeably.
- AWS credentials must come from an IAM role, AWS profile, or environment-based provider. Never commit credentials.

```text
bmw-executive-analytics-dashboard-pattabhi/
├── raw/
│   ├── dealer/dealer.csv
│   ├── maintenance/maintenance.csv
│   ├── sales/sales.csv
│   ├── telemetry/telemetry.csv
│   ├── vehicle/vehicle_master.csv
│   └── warranty/warranty.csv
├── processed/{dealer,maintenance,sales,telemetry,vehicle,warranty}/
├── curated/{dealer,maintenance,sales,telemetry,vehicle,warranty}/
├── rejected/{dealer,maintenance,sales,telemetry,vehicle,warranty}/
├── logs/
└── athena/
```

S3 folders are prefix markers, not real directories. Terraform manages the empty folder markers with `aws_s3_object.prefixes`; uploaded data objects must not be managed as Terraform resources.

The six current raw CSV objects are:

```text
raw/dealer/dealer.csv
raw/maintenance/maintenance.csv
raw/sales/sales.csv
raw/telemetry/telemetry.csv
raw/vehicle/vehicle_master.csv
raw/warranty/warranty.csv
```

## 5. Data Domains and Rules

### vehicle_master

Columns: `vehicle_id`, `vin`, `model`, `model_year`, `fuel_type`, `region`, `manufacturing_date`.

- `vehicle_id` is required and unique.
- `vin` is required and unique where available.
- `model` is required.
- `model_year` is a four-digit year.
- `region` must be `North`, `South`, `East`, or `West`.
- `manufacturing_date` must be a valid ISO date.

### telemetry

Columns: `event_id`, `vehicle_id`, `timestamp`, `speed`, `battery_level`, `temperature`, `odometer`, `latitude`, `longitude`, `fault_code`.

- `event_id` is required and unique.
- `vehicle_id` must exist in vehicle master.
- `timestamp` must be valid.
- `speed` must be non-negative.
- `battery_level` must be between 0 and 100.
- `temperature` must be between -50 and 150 C.
- `odometer` must be non-negative and non-decreasing per vehicle when ordered by timestamp.
- A non-null `fault_code` counts as a critical fault.

### sales

Columns: `sale_id`, `vehicle_id`, `dealer_id`, `customer_id`, `sale_date`, `model`, `region`, `price`, `quantity`.

- `sale_id` is required and unique.
- `vehicle_id` and `dealer_id` must be valid references.
- `sale_date` must be valid.
- `price` must be non-negative.
- `quantity` must be positive.
- Derived field: `revenue = price * quantity`.

### dealer

Columns: `dealer_id`, `dealer_name`, `city`, `region`, `capacity`, `rating`.

- `dealer_id` is required and unique.
- `region` must use the four controlled region values.
- Capacity and rating must be within sensible non-negative ranges.

### maintenance

Columns: `service_id`, `vehicle_id`, `dealer_id`, `service_date`, `service_type`, `odometer`, `parts_cost`, `labour_cost`, `failure_code`.

- `service_id` is required and unique.
- Vehicle and dealer references must be valid.
- Date must be valid.
- Costs and odometer must be non-negative.
- Derived field: `service_cost = parts_cost + labour_cost`.

### warranty

Columns: `claim_id`, `vehicle_id`, `claim_date`, `component`, `claim_amount`, `claim_status`.

- `claim_id` is required and unique.
- `vehicle_id` must be valid.
- Date must be valid.
- `claim_amount` must be non-negative.
- `claim_status` must be `Open`, `Approved`, `Rejected`, or `Paid`.

## 6. Data Pipeline Contract

Implement an idempotent batch pipeline with this flow:

1. Discover or receive a raw S3 object.
2. Load the CSV with schema checks and source metadata.
3. Validate file-level schema before row-level processing.
4. Validate required values, types, dates, ranges, duplicate keys, and references.
5. Keep valid records and add derived fields and partition fields.
6. Write valid records as Parquet under `curated/{dataset}/` or `processed/{dataset}/` according to the Athena contract.
7. Write invalid records under `rejected/{dataset}/` with source key, row number, rejection reason, and ingestion timestamp.
8. Emit structured logs and CloudWatch metrics.
9. Never overwrite a successful partition without an explicit idempotency strategy.
10. Make rerunning the same source object safe and deterministic.

The existing `src/` modules are building blocks only. A missing orchestrator must connect all six datasets, enforce dependency order with vehicle and dealer master data first, and publish outputs to S3.

## 7. KPI Definitions

The seven dashboard KPI cards are:

1. Revenue: `SUM(price * quantity)`.
2. Sales: `SUM(quantity)`.
3. Vehicles: `COUNT(DISTINCT vehicle_id)`.
4. Average battery: `AVG(battery_level)`.
5. Critical faults: telemetry records where `fault_code IS NOT NULL`.
6. Warranty cost: `SUM(claim_amount)`.
7. Service volume: `COUNT(DISTINCT service_id)`.

All KPI calculations must reconcile between Python, Athena, and QuickSight. Avoid duplicate joins that multiply measures.

## 8. Athena and QuickSight Requirements

Athena must provide:

- Database `bmw_analytics`.
- External tables for vehicle master, telemetry, dealer, sales, maintenance, and warranty.
- Date partitions: telemetry by `event_date`; sales by `sale_month`; maintenance by `service_month`; warranty by `claim_month`.
- View `bmw_analytics.vw_executive_kpis` for regional trends and KPI consumption.
- Query result encryption and a controlled workgroup with a bytes-scanned limit.

Important current issue: `sql/001_create_database.sql` hardcodes `s3://bmw-executive-dashboard/...`, but the deployed bucket is `s3://bmw-executive-analytics-dashboard-pattabhi/...`. Parameterize the bucket or generate the SQL from the configured bucket before running Athena.

QuickSight must provide:

- Seven KPI cards.
- Revenue, sales, warranty, and service trends.
- Revenue by region, faults by region, warranty cost by region, top models, and top dealers.
- Controls for region, dealer, model, and date range.
- Drill-down: BMW > Region > Dealer > Model.
- Visible last-refresh timestamp and clear zero-data states.
- Currency and percentage formatting.
- SPICE import after Athena row-count and freshness validation.

Regional RLS rules:

```text
south.manager -> South
north.manager -> North
east.manager  -> East
west.manager  -> West
executives    -> unrestricted executive group
```

Test both direct dataset access and visual results for every role.

## 9. Security and Operations

- Keep the S3 bucket private.
- Keep public access blocks enabled.
- Use SSE-S3 or SSE-KMS, versioning, and TLS-only bucket access.
- Use least-privilege IAM policies.
- Use GitHub Actions OIDC instead of long-lived AWS keys.
- Never log credentials, full VINs, customer IDs, or raw payloads.
- Do not manually edit curated data; correct the source or pipeline and rerun.

CloudWatch namespace: `BMW/ExecutiveAnalytics`.

Required metrics: `RecordsProcessed`, `ValidationFailures`, `ProcessingFailures`, `ExecutionDurationMs`, `FilesProcessed`, and `DataFreshnessHours`, with `Dataset` and `Environment` dimensions.

Alarms:

- Any processing failure.
- Validation failure rate above 5%.
- Runtime above p95 baseline by 25%.
- Data freshness above 30 hours.

Structured log fields: `run_id`, `dataset`, `source_key`, `records_in`, `records_out`, `records_rejected`, `duration_ms`, and `error_type`.

## 10. Current Implementation Status

Completed:

- Deterministic sample data generation in `generate_data.py`.
- Local CSV loader.
- Basic telemetry, required-column, and vehicle-reference validation.
- Sales and maintenance derived-field helpers.
- Seven Python KPI functions except the service-volume test import coverage is incomplete.
- Unit tests for KPI functions and one validation path.
- S3 bucket Terraform baseline with versioning, AES256 encryption, public access blocks, and folder markers.
- Six raw CSV files uploaded to the current S3 bucket.
- Basic GitHub Actions lint, test, package, and SQL sync workflow.

Incomplete and must be implemented:

- Full validation for all six domains and all documented rules.
- Rejection metadata and durable rejected-zone output.
- S3-to-curated batch orchestration.
- Parquet writing, partitioning, and idempotency.
- Correct bucket parameterization in Athena SQL.
- Athena deployment, workgroup, partitions, and query-result configuration.
- QuickSight dataset, visuals, controls, calculated fields, refresh, and RLS.
- CloudWatch logs, metrics, alarms, and SNS routing.
- TLS-only bucket policy, lifecycle policy, and complete least-privilege IAM.
- End-to-end reconciliation and UAT evidence.
- Coverage target of at least 80% for Python code.

## 11. Recommended Implementation Order

1. Fix bucket configuration so Terraform, Python, Athena SQL, and CI use one source of truth.
2. Add complete schema definitions and domain validators.
3. Add a pipeline runner that processes raw S3 files and writes Parquet/rejected outputs.
4. Add unit and integration tests using the generated sample data.
5. Parameterize and deploy Athena DDL, partitions, KPI queries, and views.
6. Reconcile Python KPI results against Athena results.
7. Build QuickSight dataset, dashboard, filters, drill-down, and RLS.
8. Add CloudWatch metrics, alarms, structured logs, and an operational runbook.
9. Harden Terraform and IAM, then run security review.
10. Run UAT for executives and each regional manager role.
11. Update README and documentation with actual deployment commands and evidence.

## 12. Validation and Acceptance Checklist

Run locally before proposing completion:

```powershell
python -m pytest -q
ruff check src tests
python -m compileall src
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
```

Acceptance requires:

- A representative raw load produces valid curated data and rejected rows.
- Invalid rows contain source and reason metadata.
- Athena totals reconcile to independent Python calculations.
- QuickSight totals match Athena and all controls work.
- Regional managers cannot see another region.
- Daily refresh completes by 06:00 local time and displays freshness.
- CI blocks merges on lint, test, compile, or package failure.
- CloudWatch alerts on failure, stale data, runtime regression, or excessive validation failures.

## 13. Copilot Working Rules

- Inspect nearby code and existing documentation before changing architecture.
- Prefer the repository's existing Python, pandas, boto3, Terraform, Athena, and GitHub Actions patterns.
- Keep changes small, typed, testable, and idempotent.
- Do not add secrets, hardcoded credentials, or unrelated refactors.
- Preserve public APIs unless the task explicitly requires a breaking change.
- Add focused tests for each new validation rule, transformation, KPI, and pipeline behavior.
- Treat data-quality failures as data outputs, not silent drops.
- Use UTC timestamps for ingestion metadata and make timezone assumptions explicit.
- Do not claim an AWS or QuickSight feature is complete until it has been deployed or verified.
- When reporting status, separate implemented, deployed, verified, and still missing work.