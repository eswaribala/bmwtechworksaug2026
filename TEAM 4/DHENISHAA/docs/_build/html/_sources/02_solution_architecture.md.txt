# 02. Solution Architecture

## Overview
The solution uses AWS-managed services to create a serverless data lake for BMW-style vehicle analytics.

## Layers
- Source data generation
- Raw landing zone in S3
- Data validation and transformation
- Curated Parquet layer
- AWS Glue catalog
- Athena SQL analysis
- QuickSight visualization
- Lake Formation governance
- CloudWatch monitoring

## Core design decisions
- Use S3 as the durable storage layer.
- Use Parquet because it is columnar and efficient for analytics.
- Partition by year and month for telemetry queries.
- Keep raw and curated data distinct to preserve lineage.
- Use Terraform to provision and document infrastructure.
