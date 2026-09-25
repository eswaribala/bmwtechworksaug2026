# Solution Architecture

## Logical flow

CSV files land in an S3 raw zone. A Python batch validates schema, keys, dates, ranges, and duplicates. Valid records are normalized and written to processed/curated Parquet; invalid records retain the source filename, row number, rejection reason, and ingestion timestamp in `rejected/`. Athena exposes partitioned tables and a small set of governed views. QuickSight consumes the views with SPICE refreshes and regional row-level security.

## AWS components

| Layer | Service | Responsibility |
|---|---|---|
| Storage | S3 | Raw, processed, curated, rejected, SQL, and audit prefixes |
| Compute | Python batch, optional Lambda/Glue | Validate, transform, and publish Parquet |
| Query | Athena | Serverless SQL over curated data |
| BI | QuickSight | Dataset, calculated fields, dashboard, RLS |
| Observability | CloudWatch | Logs, metrics, alarms, dashboards |
| Delivery | GitHub Actions + OIDC | Test, package, and deploy SQL/artifacts |
| IaC | Terraform | Repeatable S3 and later IAM/Athena resources |

## S3 layout

`raw/{sales,telemetry,vehicle,maintenance,warranty}/`, `processed/{dataset}/`, `curated/{dataset}/`, `rejected/{dataset}/`, `logs/`, and `athena/`.

Use SSE-S3 or SSE-KMS, versioning, lifecycle transitions to Glacier for old raw data, and a bucket policy that denies non-TLS requests and public access.

## Data flow and failure handling

The batch emits `records_processed`, `validation_failures`, `processing_failures`, and `execution_duration_ms`. A failed file is isolated, logged with a correlation ID, and does not overwrite the previous successful partition. Rejected rows are reviewable without blocking valid rows unless schema validation fails at file level.

## AWS setup sequence

Create S3 and KMS, create an Athena workgroup with query-result encryption and a bytes-scanned limit, create an IAM execution role, deploy the validator as a scheduled ECS task/Glue job or Lambda for small files, create Athena tables, then connect QuickSight. Grant QuickSight only `GetObject` on curated prefixes and Athena query access to the workgroup.
