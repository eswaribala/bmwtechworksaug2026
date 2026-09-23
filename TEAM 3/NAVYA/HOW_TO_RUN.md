# BMW Enterprise Batch ETL — How to Run.

This guide explains how to run the BMW Enterprise Batch ETL project on a Windows laptop.

---

## 1. Requirements

Install or have available:

- Python 3.12
- Java 21
- Git
- Docker Desktop

The project uses:

- PySpark
- FastAPI
- React
- Docker
- Pytest
- Sphinx

---

## 2. Clone the Repository

```powershell
git clone https://github.com/NavyaS-0/bmw-enterprise-batch-etl.git
cd bmw-enterprise-batch-etl
```

---

## 3. Create Python Environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 4. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 5. Run the ETL Pipeline

```powershell
python -m src.processing.etl_pipeline
```

The pipeline:

1. Reads the BMW CSV datasets.
2. Applies schemas.
3. Performs data-quality checks.
4. Rejects invalid records.
5. Removes duplicates.
6. Applies business transformations.
7. Generates Parquet datasets.
8. Partitions Sales data by region.
9. Writes rejected records separately.
10. Creates application logs.

Generated outputs:

```text
data/
├── processed/
└── rejected/
```

These generated folders are intentionally excluded from Git.

---

## 6. Run Automated Tests

```powershell
pytest -q
```

Expected result:

```text
5 passed
```

The tests validate:

- Processed vehicle data
- Vehicle ID uniqueness
- Sales revenue calculation
- Positive sales quantity
- Maintenance cost calculation

---

## 7. Start the FastAPI Backend

Run:

```powershell
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/health
```

API documentation:

```text
http://localhost:8000/docs
```

The API provides:

- KPI summary
- Model analytics
- Regional analytics
- Maintenance analytics
- Dealer analytics

Keep this terminal running.

---

## 8. Start the React Dashboard

Open a **second PowerShell terminal**.

Go to the project:

```powershell
cd bmw-enterprise-batch-etl
```

Make sure Docker Desktop is running.

Run:

```powershell
docker compose up --build
```

Open:

```text
http://localhost:3000
```

The dashboard displays:

- Total revenue
- Vehicles sold
- Revenue by model
- Revenue by region
- Maintenance analytics
- Dealer analytics
- Data-quality information
- ETL pipeline information

---

## 9. View Sphinx Documentation

Sphinx source files are located at:

```text
docs/sphinx/source/
```

Rebuild the documentation:

```powershell
sphinx-build -b html .\docs\sphinx\source .\docs\sphinx\build\html
```

Open the generated documentation:

```powershell
Start-Process ".\docs\sphinx\build\html\index.html"
```

---

## 10. AWS Analytics

The project uses:

| Component | Configuration |
|---|---|
| AWS Region | `eu-north-1` |
| S3 Bucket | `bmw-enterprise-etl-navya-2026` |
| Glue Database | `bmw_enterprise_etl` |
| Analytics | Amazon Athena |

Amazon Athena is used to query the curated Parquet datasets and generate business analytics.

---

## 11. Athena SQL

SQL analysis files are available under:

```text
sql/
```

They include:

- Row-count validation
- Sales KPIs
- Revenue by model
- Revenue by region
- Maintenance analysis
- Top dealers by revenue

---

## 12. Terraform

Terraform configuration is available under:

```text
terraform/
```

Validate the configuration:

```powershell
cd terraform
terraform init
terraform validate
terraform plan
```

Some AWS resources could not be managed through Terraform because of restrictions in the BMW training AWS account.

The Terraform configurations were validated, but restricted resources were not force-applied.

No AWS permissions were bypassed.

---

## 13. Project Flow

```text
BMW CSV Data
     |
     v
PySpark ETL
     |
     +------ Invalid Records ------> Rejected
     |
     v
Processed Parquet
     |
     v
AWS S3
     |
     v
Glue Catalog
     |
     v
Amazon Athena
     |
     v
Business KPIs
     |
     v
FastAPI
     |
     v
React Dashboard
```

---

## 14. Stop the Project

Stop FastAPI:

```text
Ctrl + C
```

Stop Docker:

```powershell
docker compose down
```

---

## 15. Project Documentation

Additional documentation is available in:

```text
README.md
docs/PRD.md
docs/ARCHITECTURE.md
docs/DATA_DICTIONARY.md
docs/sphinx/
```

---

## Expected Result

After following this guide, a reviewer should be able to:

1. Run the PySpark ETL pipeline.
2. Generate processed and rejected datasets.
3. Run the automated tests.
4. Start the FastAPI backend.
5. Open the API documentation.
6. Start the React dashboard through Docker.
7. View the BMW analytics dashboard.
8. View the Sphinx technical documentation.
9. Review the Athena SQL queries.
10. Review the Terraform configuration.