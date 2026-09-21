\# BMW Enterprise Batch ETL



A reusable BMW batch data engineering pipeline that validates, transforms, and prepares multiple BMW datasets for analytics.



\## Project Flow



CSV → S3 Raw → PySpark ETL → Data Quality

&#x20;                        ↓

&#x20;               ┌────────┴────────┐

&#x20;               ↓                 ↓

&#x20;         Processed Parquet   Rejected Records

&#x20;               ↓

&#x20;         Glue Data Catalog

&#x20;               ↓

&#x20;            Athena

&#x20;               ↓

&#x20;          FastAPI API

&#x20;               ↓

&#x20;         React Dashboard



\# BMW Enterprise Batch ETL



A reusable BMW batch data engineering pipeline that validates, transforms, and prepares multiple BMW datasets for analytics.



\---



\## Datasets



The platform processes four BMW datasets:



\- \*\*Vehicle Master\*\*

\- \*\*Sales\*\*

\- \*\*Maintenance\*\*

\- \*\*Dealer\*\*



\---



\## Key Features



\- PySpark-based ETL processing

\- Schema and data-quality validation

\- Null and duplicate handling

\- Invalid-record rejection

\- Business-rule validation

\- Parquet conversion

\- Sales partitioning by region

\- AWS S3, Glue, and Athena integration

\- FastAPI backend

\- React dashboard

\- Automated testing with Pytest

\- Application logging

\- Docker deployment

\- GitHub Actions CI/CD

\- Terraform infrastructure configuration



\---



\## Data Quality Results



| Dataset | Raw Records | Rejected | Processed |

|---|---:|---:|---:|

| Vehicle Master | 1,000 | 2 | 997 |

| Sales | 1,000 | 3 | 996 |

| Maintenance | 1,000 | 2 | 997 |

| Dealer | 100 | 2 | 97 |



\---



\## Business KPIs



The platform provides the following business analytics:



\- Total revenue

\- Vehicles sold

\- Revenue by model

\- Revenue by region

\- Maintenance cost analysis

\- Top dealers by revenue



\### Example Results



| KPI | Value |

|---|---:|

| Total Revenue | ₹190,171,659.30 |

| Vehicles Sold | 2,007 |



\---



\## Run Locally



\### 1. Install Dependencies



```powershell

pip install -r requirements.txt



2\. Run ETL Pipeline

python -m src.processing.etl\_pipeline

3\. Run Automated Tests

pytest -q



Expected result:



5 passed

4\. Start FastAPI

python -m uvicorn src.api.main:app --reload --port 8000



API documentation:



http://localhost:8000/docs

5\. Start Dashboard

docker compose up --build



Open the dashboard:



http://localhost:3000

AWS

Component	Configuration

Region	eu-north-1

S3 Bucket	bmw-enterprise-etl-navya-2026

Glue Database	bmw\_enterprise\_etl

Analytics	Amazon Athena



Athena is used to query the curated Parquet datasets and generate business KPIs.



Project Structure

bmw-enterprise-batch-etl/

│

├── data/

├── docs/

├── frontend/

├── src/

├── sql/

├── terraform/

├── tests/

├── .github/

│

├── docker-compose.yml

├── HOW\_TO\_RUN.md

├── README.md

└── requirements.txt

Documentation

Document	Description

docs/PRD.md	Product requirements

docs/ARCHITECTURE.md	System architecture

docs/DATA\_DICTIONARY.md	Dataset and field definitions

HOW\_TO\_RUN.md	Setup and execution guide

Terraform



Terraform configuration is available under:



terraform/



The configuration has been validated using:



terraform init

terraform validate

terraform plan



Some AWS resources could not be managed through Terraform because of restrictions in the BMW training AWS account. The resources were plan-validated but not applied through Terraform.



No permissions were bypassed.



Security

No AWS credentials are stored in the repository.

.env files are excluded from Git.

Terraform state files are excluded from Git.

Generated logs are excluded from Git.

Local virtual environments are excluded from Git.

