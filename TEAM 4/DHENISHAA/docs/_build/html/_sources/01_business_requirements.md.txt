# 01. Business Requirements

## Business objective
The BMW Serverless Data Lake project is designed to provide a scalable, cost-aware analytics platform for vehicle telemetry, sell-through, maintenance, and warranty data.

## Business stakeholders
- Data engineering teams
- Product and fleet analytics teams
- Warranty and service teams
- Operations and engineering leaders

## Requirements
1. Store raw BMW-like data in S3.
2. Separate raw and curated data layers.
3. Use automated processing to clean and normalize data.
4. Convert data to Parquet and partition effectively.
5. Catalog data with AWS Glue.
6. Query data with Athena.
7. Apply governance with Lake Formation.
8. Enable dashboards with QuickSight.
9. Support auditability and operational monitoring.

## Acceptance criteria
The solution must demonstrate a measurable reduction in data scanned through effective Parquet and partition design.
