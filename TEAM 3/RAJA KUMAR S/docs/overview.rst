Project Overview
=================

Modern BMW systems generate data from multiple sources such as connected
vehicles, vehicle telemetry, sales systems, dealers, maintenance systems,
warranty systems, charging sessions, and customer feedback.

These datasets can contain:

- Missing values
- Duplicate records
- Invalid vehicle IDs / VINs
- Invalid dates
- Out-of-range values
- Referential-integrity violations

The **BMW Data Quality & Governance Platform** validates incoming data before
it is consumed by downstream analytical systems. It separates valid and
invalid data, calculates a Data Quality Score, generates a quality report,
and provides operational visibility through CloudWatch.

Business Problem
-----------------

BMW data engineers need visibility into the quality of incoming datasets.
Poor-quality data can lead to incorrect analytics, incorrect business KPIs,
invalid reports, faulty downstream processing, unreliable dashboards, and
data inconsistencies between systems.

The platform answers: **"Can BMW trust this dataset for downstream
analytics?"** — with a measurable Data Quality Score from 0-100.

Objectives
----------

1. Ingest BMW datasets.
2. Store raw data in Amazon S3.
3. Validate incoming data.
4. Detect data-quality issues.
5. Separate valid and invalid records.
6. Quarantine bad records.
7. Calculate a Data Quality Score.
8. Generate a quality report.
9. Register datasets using AWS Glue Catalog.
10. Make curated data queryable using Athena.
11. Provide operational logging through CloudWatch.
12. Implement automated tests.
13. Provide reproducible deployment and execution instructions.

Technology Stack
-----------------

============================  ===================================
Layer                         Technology
============================  ===================================
Programming                   Python
Distributed Processing        PySpark
Cloud Storage                 Amazon S3
Data Catalog                  AWS Glue Data Catalog
Governance                    AWS Lake Formation
Analytics                     Amazon Athena
Monitoring                    Amazon CloudWatch
Testing                       Pytest
Backend API                   FastAPI
Frontend                      React + TypeScript (Vite)
Infrastructure as Code        Terraform
Version Control               Git / GitHub
Data Format                   CSV / Parquet
============================  ===================================
