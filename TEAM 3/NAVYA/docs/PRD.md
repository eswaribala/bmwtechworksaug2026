\# Product Requirements Document (PRD)



\## BMW Enterprise Batch ETL Platform



\### 1. Product Overview



The BMW Enterprise Batch ETL Platform is a reusable data engineering solution for processing multiple BMW business datasets and converting raw CSV data into validated, analytics-ready Parquet data.



The platform supports:



\- Data ingestion from AWS S3

\- Schema validation

\- Null and data-quality validation

\- Duplicate detection and removal

\- Invalid-record rejection

\- Data transformation

\- Parquet conversion

\- Region-based partitioning for sales data

\- AWS Glue Data Catalog integration

\- Amazon Athena analytics

\- FastAPI analytics APIs

\- React-based business dashboard

\- Automated testing

\- Application logging

\- Docker-based frontend deployment

\- Terraform infrastructure definitions

\- CI/CD validation through GitHub Actions



\---



\## 2. Business Problem



BMW business data can originate from multiple operational datasets such as vehicle master, sales, maintenance, and dealer information.



Raw data may contain:



\- Missing values

\- Duplicate records

\- Invalid dates

\- Invalid numeric values

\- Invalid ranges

\- Inconsistent records



Without a reusable processing pipeline, preparing these datasets for analytics can require repeated manual processing.



The goal of this project is to provide a reusable batch ETL pipeline that validates, cleans, transforms, and prepares BMW datasets for downstream analytics.



\---



\## 3. Product Goal



Build a reliable batch data pipeline that transforms raw BMW CSV datasets into trusted, analytics-ready data that can be queried through Amazon Athena and consumed by an API and dashboard.



The target data flow is:



S3 Raw CSV

→ PySpark ETL

→ Data Quality Validation

→ Rejected Records

→ Processed Parquet

→ AWS Glue Data Catalog

→ Amazon Athena

→ FastAPI

→ React Dashboard



\---



\## 4. Datasets



The platform processes four BMW datasets.



\### Vehicle Master



Contains vehicle-level information such as:



\- Vehicle ID

\- VIN

\- Model

\- Model year

\- Fuel type

\- Region

\- Manufacturing date



\### Sales



Contains sales transaction information such as:



\- Sale ID

\- Vehicle ID

\- Dealer ID

\- Customer ID

\- Sale date

\- Model

\- Region

\- Price

\- Quantity



The ETL pipeline also calculates:



`revenue = price × quantity`



Sales data is partitioned by region in the processed Parquet output.



\### Maintenance



Contains vehicle maintenance information such as:



\- Service ID

\- Vehicle ID

\- Dealer ID

\- Service date

\- Service type

\- Odometer

\- Parts cost

\- Labour cost

\- Failure code



The ETL pipeline calculates:



`total\_service\_cost = parts\_cost + labour\_cost`



\### Dealer



Contains dealer information such as:



\- Dealer ID

\- Dealer name

\- City

\- Region

\- Capacity

\- Rating



\---



\## 5. Functional Requirements



\### FR-01 — Data Ingestion



The system shall read BMW CSV datasets from the configured raw data location.



\### FR-02 — Schema Validation



The system shall apply explicit schemas to the datasets instead of relying only on automatic type inference.



\### FR-03 — Null Validation



The system shall identify records containing required null values.



\### FR-04 — Duplicate Detection



The system shall identify duplicate business keys.



Examples:



\- Vehicle ID

\- Sale ID

\- Service ID

\- Dealer ID



\### FR-05 — Data Range Validation



The system shall identify invalid numeric values.



Examples:



\- Vehicle model year outside the accepted range

\- Negative sales price

\- Invalid quantity

\- Negative maintenance costs

\- Dealer rating outside the accepted range



\### FR-06 — Date Validation



The system shall identify invalid or missing date values.



\### FR-07 — Rejected Records



Invalid records shall be separated from valid records and stored in the rejected-data output.



\### FR-08 — Deduplication



Valid records shall be deduplicated using their relevant business keys.



\### FR-09 — Transformation



The pipeline shall calculate business fields required for analytics.



Examples:



\- Sales revenue

\- Maintenance total service cost



\### FR-10 — Parquet Conversion



Validated datasets shall be converted to Parquet format.



\### FR-11 — Partitioning



Sales data shall be partitioned by region to improve organization and support analytical querying.



\### FR-12 — Analytics



The processed datasets shall be queryable through Amazon Athena.



\### FR-13 — API



FastAPI shall expose processed business KPIs.



\### FR-14 — Dashboard



The React dashboard shall display business KPIs and analytical information.



\### FR-15 — Testing



The project shall contain automated tests covering processed-data existence, uniqueness, calculations, and data-quality rules.



\### FR-16 — Logging



The ETL pipeline shall generate application logs for successful processing and errors.



\---



\## 6. Business KPIs



The platform provides business analytics including:



\### Sales KPIs



\- Total revenue

\- Total vehicles sold

\- Total sales records

\- Revenue by BMW model

\- Vehicles sold by BMW model

\- Revenue by region

\- Vehicles sold by region



\### Maintenance KPIs



\- Total maintenance records

\- Total maintenance cost

\- Maintenance cost by service type

\- Service count by service type



\### Dealer KPIs



\- Top dealers by revenue

\- Vehicles sold by dealer

\- Dealer city and region



\---



\## 7. Non-Functional Requirements



\### Reliability



The pipeline shall handle invalid records without stopping the entire processing workflow where possible.



\### Maintainability



The solution shall use modular Python/PySpark code with separate areas for:



\- Ingestion

\- Validation

\- Processing

\- Transformation

\- Utilities

\- API



\### Reproducibility



The project shall contain documented instructions for setting up and running the pipeline.



\### Security



The project shall not contain AWS access keys, passwords, or other secrets in source control.



\### Observability



The application shall provide structured application logging and error handling.



\### Portability



The ETL pipeline shall use environment-based Java configuration where available, with a local fallback for the development environment.



\---



\## 8. API Requirements



The FastAPI service shall provide:



| Endpoint | Purpose |

|---|---|

| `/` | API information |

| `/health` | Health check |

| `/api/kpis/summary` | Overall sales and maintenance KPIs |

| `/api/kpis/models` | Sales and revenue by model |

| `/api/kpis/regions` | Sales and revenue by region |

| `/api/kpis/maintenance` | Maintenance cost by service type |

| `/api/kpis/dealers` | Top 10 dealers by revenue |



\---



\## 9. Dashboard Requirements



The React dashboard shall provide:



\- API connectivity status

\- KPI cards

\- Revenue analysis

\- Model-level analysis

\- Regional analysis

\- Maintenance analysis

\- Dealer analysis

\- Interactive filtering

\- Data-quality information

\- ETL pipeline status/visualization



The dashboard is served through Nginx and can be started using Docker Compose.



\---



\## 10. Data Quality Rules



Examples of invalid records include:



\### Vehicle Master



\- Missing vehicle ID

\- Missing model year

\- Model year outside the accepted range

\- Duplicate vehicle ID



\### Sales



\- Missing sale ID

\- Missing vehicle ID

\- Missing sale date

\- Missing price

\- Invalid or negative price

\- Invalid quantity

\- Duplicate sale ID



\### Maintenance



\- Missing service ID

\- Missing vehicle ID

\- Missing service date

\- Missing cost values

\- Negative maintenance costs

\- Duplicate service ID



\### Dealer



\- Missing dealer ID

\- Missing dealer name

\- Missing city

\- Missing region

\- Invalid capacity

\- Dealer rating outside the accepted 0–5 range

\- Duplicate dealer ID



\---



\## 11. Expected Processing Outcome



The sample datasets contain intentionally invalid and duplicate records to demonstrate the data-quality process.



The latest local ETL run produced:



| Dataset | Raw Records | Rejected | Valid After Rejection | Final Clean Records |

|---|---:|---:|---:|---:|

| Vehicle Master | 1000 | 2 | 998 | 997 |

| Sales | 1000 | 3 | 997 | 996 |

| Maintenance | 1000 | 2 | 998 | 997 |

| Dealer | 100 | 2 | 98 | 97 |



\---



\## 12. Acceptance Criteria



The product is considered functionally complete when:



1\. Raw BMW CSV datasets can be processed by the ETL pipeline.

2\. Explicit schemas are applied.

3\. Invalid records are identified and separated.

4\. Duplicate records are removed.

5\. Business transformations are calculated.

6\. Processed datasets are generated as Parquet.

7\. Sales data is partitioned by region.

8\. Rejected datasets are generated.

9\. Processed data is available for Athena analysis.

10\. Athena can query the curated datasets.

11\. FastAPI can return business KPIs.

12\. The React dashboard can display the API data.

13\. Automated tests pass.

14\. Application logging is generated.

15\. The project can be reproduced using the documented setup instructions.

16\. No credentials or secrets are stored in the repository.



\---



\## 13. AWS Infrastructure



The solution uses:



\- Amazon S3 for raw and processed data

\- AWS Glue Data Catalog for metadata

\- Amazon Athena for analytical queries



Terraform configuration is included for infrastructure definitions.



During development, the training AWS account applied explicit IAM restrictions to several AWS read/create operations. Terraform configurations were therefore validated using `terraform plan`, but resources affected by these account restrictions were not applied through Terraform.



Existing AWS S3, Glue, and Athena resources used by the project remain documented separately.



\---



\## 14. Project Success



The project succeeds when the complete flow can be demonstrated:



Raw BMW datasets

→ Data quality validation

→ Clean and rejected outputs

→ Processed Parquet

→ Athena analytics

→ FastAPI

→ React dashboard



The repository contains the source code, tests, SQL queries, infrastructure definitions, configuration, and documentation required to understand and reproduce the solution.

