# BMW Warranty Claims Analytics

An end-to-end data engineering and analytics project for processing, validating, enriching, and analyzing BMW warranty claims.

## Project Overview

This project implements a complete warranty analytics pipeline using AWS, PySpark, SQL, Snowflake, and Amazon QuickSight.

The pipeline processes warranty claims and vehicle master data, performs data quality validation, enriches valid claims with vehicle information, stores processed data in Amazon S3, and provides analytical insights through Athena, Snowflake, and QuickSight.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and processing code |
| PySpark | Data validation and transformation |
| Amazon S3 | Cloud data storage |
| AWS Glue | Data Catalog |
| Amazon Athena | SQL querying |
| Terraform | Infrastructure as Code |
| Snowflake | Data warehouse and analytics |
| Amazon QuickSight | Dashboard and visualization |
| pytest | Automated testing |
| Sphinx | Project documentation |

## Architecture

```text
Source CSV Files
       |
       v
   Amazon S3
    Raw Data
       |
       v
    PySpark
   Validation
       |
       +------------------+
       |                  |
       v                  v
 Valid Records      Rejected Records
       |
       v
 PySpark Enrichment
       |
       v
 Amazon S3
 Processed Parquet
       |
       +------------------+
       |                  |
       v                  v
    Athena           Snowflake
       |                  |
       |             SQL Analytics
       |                  |
       +--------+---------+
                |
                v
          QuickSight
           Dashboard
```

## Data Flow

### 1. Raw Data

The project uses two source datasets:

- `warranty_claims.csv`
- `vehicle_master.csv`

The raw files are stored in Amazon S3 under:

```text
raw/warranty/
raw/vehicle_master/
```

### 2. PySpark Validation

PySpark validates the warranty claim records for:

- Missing claim IDs
- Invalid claim dates
- Negative claim amounts
- Unknown vehicle IDs
- Required field validation

Valid records are stored in:

```text
processed/warranty_valid/
```

Rejected records are stored in:

```text
processed/warranty_rejected/
```

### 3. Data Enrichment

Valid warranty claims are joined with vehicle master data.

The enriched data contains information such as:

- VIN
- Vehicle model
- Model year
- Fuel type
- Region

The enriched dataset is stored in:

```text
processed/warranty_enriched/
```

The processed datasets are stored in Apache Parquet format.

---

## AWS Infrastructure

Terraform is used to provision and manage the AWS infrastructure.

### Amazon S3

The main S3 bucket is:

```text
bmw-warranty-claims-532404260630
```

The bucket contains the following logical structure:

```text
raw/
├── warranty/
│   └── warranty_claims.csv
└── vehicle_master/
    └── vehicle_master.csv

processed/
├── warranty_valid/
├── warranty_rejected/
└── warranty_enriched/

athena-results/
```

### AWS Glue

AWS Glue Data Catalog provides metadata for the processed datasets.

Database:

```text
bmw_warranty_analytics
```

Tables:

- `warranty_valid`
- `warranty_enriched`
- `warranty_rejected`

### Terraform

Terraform manages the AWS infrastructure as Infrastructure as Code.

The configuration includes:

- Amazon S3 bucket
- S3 versioning
- S3 server-side encryption
- S3 public access blocking
- AWS Glue database
- AWS Glue tables

Common Terraform commands:

```powershell
terraform init
terraform validate
terraform plan
terraform apply
```

---

## PySpark Processing

PySpark is used as the main data processing engine.

The processing pipeline performs:

1. Loading warranty claims from Amazon S3
2. Loading vehicle master data from Amazon S3
3. Schema validation
4. Data quality validation
5. Separating valid and rejected records
6. Enriching valid claims with vehicle information
7. Writing processed datasets to Amazon S3 in Parquet format

### Validation Rules

| Validation | Description |
|---|---|
| Claim ID | Claim ID must be present |
| Vehicle ID | Vehicle must exist in vehicle master |
| Claim Amount | Claim amount cannot be negative |
| Claim Date | Claim date must be valid |
| Required fields | Required fields must contain valid values |

### Validation Results

The successful validation pipeline processed:

| Dataset | Records |
|---|---:|
| Warranty records read | 1,500 |
| Vehicle records read | 200 |
| Valid records | 1,496 |
| Rejected records | 4 |
| Enriched records | 1,496 |

The rejected records included the following validation issues:

- Vehicle not found in vehicle master
- Negative claim amount
- Missing claim ID
- Invalid claim date

### PySpark Script

The main validation pipeline is:

```text
src/processing/validate_warranty.py
```

Spark can be tested using:

```powershell
python .\src\processing\test_spark.py
```

S3 connectivity can be tested using:

```powershell
python .\src\processing\test_s3_spark.py
```

---

## Amazon Athena

Amazon Athena is used to query the processed Parquet datasets using SQL.

Athena database:

```text
bmw_warranty_analytics
```

Example query:

```sql
SELECT COUNT(*) AS total_claims
FROM warranty_valid;
```

The processed valid dataset contains:

```text
1,496 records
```

Athena provides serverless SQL analysis directly on the processed data stored in Amazon S3.

---

## Snowflake

Snowflake is used as the data warehouse and analytical layer.

### Database and Schema

Database:

```text
BMW_WARRANTY_ANALYTICS
```

Schema:

```text
WARRANTY
```

Main table:

```text
WARRANTY_CLAIMS
```

The Snowflake table contains the processed valid warranty claim data.

### Snowflake Components

The project includes:

- Snowflake warehouse
- Database
- Schema
- Warranty claims table
- S3 storage integration
- External stage
- Analytical views

### Analytical Views

The following views are used for analysis:

```text
COMPONENT_STATUS_SUMMARY
WARRANTY_KPI_SUMMARY
REJECTION_ANALYSIS
```

### Warranty Data Summary

The Snowflake warranty claims table contains:

```text
1,496 valid warranty claims
```

Total claim amount:

```text
3,895,096.49
```

Average claim amount:

```text
2,603.67
```

---

## Warranty Cost Analysis

The project analyzes warranty costs by vehicle component.

The component-level analysis identified the following three highest-cost components in the analyzed valid-claims dataset:

| Component | Claims | Total Warranty Cost |
|---|---:|---:|
| Engine | 249 | 1,272,385.88 |
| Transmission | 219 | 871,574.62 |
| Battery | 192 | 535,335.24 |

This analysis is implemented using SQL aggregation in Snowflake.

Example query:

```sql
SELECT
    COMPONENT,
    COUNT(*) AS CLAIM_COUNT,
    SUM(CLAIM_AMOUNT) AS TOTAL_WARRANTY_COST
FROM WARRANTY_CLAIMS
GROUP BY COMPONENT
ORDER BY TOTAL_WARRANTY_COST DESC;
```

---

## Amazon QuickSight Dashboard

Amazon QuickSight is used to visualize the warranty analytics.

The dashboard is connected to the processed warranty data through Amazon Athena.

The dashboard includes the following visualizations:

1. Total Claims
2. Total Claim Amount
3. Claims by Status
4. Total Claim Amount by Component
5. Monthly Claim Amount Trend
6. Claims by Component
7. Average Claim Amount by Claim Status
8. Average Claim Amount
9. Monthly Claim Count Trend

### Key Dashboard KPIs

| KPI | Value |
|---|---:|
| Total Claims | 1,496 |
| Total Claim Amount | 3,895,096.49 |
| Average Claim Amount | 2,603.67 |

The dashboard provides visibility into:

- Warranty claim volume
- Warranty costs
- Claim status
- Component-level costs
- Monthly trends
- Average claim amounts

---

## Testing

Automated testing is implemented using `pytest`.

The project contains tests for:

- Warranty validation
- Missing claim IDs
- Unknown vehicles
- Negative claim amounts
- Invalid claim dates
- Warranty data enrichment

The test suite can be executed with:

```powershell
python -m pytest .\tests -v
```

### Test Result

The current test suite contains:

```text
6 tests passed
```

The tests verify the core validation and transformation logic used by the PySpark processing pipeline.

Test files:

```text
tests/
├── test_analytics.py
├── test_transformation.py
└── test_validation.py
```

---

## Project Documentation

Sphinx is used to generate technical documentation for the project.

Documentation source files are located under:

```text
docs/source/
```

The documentation includes:

- Architecture
- AWS infrastructure
- PySpark processing
- Athena
- Snowflake
- QuickSight
- Testing
- Usage

### Build Documentation

Run:

```powershell
sphinx-build -b html docs/source docs/build/html
```

The generated documentation is available at:

```text
docs/build/html/index.html
```

---

## Project Structure

```text
bmw-warranty-claims-analytics/
│
├── data/
│   └── sample/
│       ├── warranty_claims.csv
│       └── vehicle_master.csv
│
├── src/
│   ├── __init__.py
│   └── processing/
│       ├── __init__.py
│       ├── test_spark.py
│       ├── test_s3_spark.py
│       └── validate_warranty.py
│
├── tests/
│   ├── test_analytics.py
│   ├── test_transformation.py
│   └── test_validation.py
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── docs/
│   ├── build/
│   └── source/
│       ├── architecture.rst
│       ├── athena.rst
│       ├── aws_infrastructure.rst
│       ├── pyspark.rst
│       ├── quicksight.rst
│       ├── snowflake.rst
│       ├── testing.rst
│       ├── usage.rst
│       ├── conf.py
│       └── index.rst
│
└── README.md
```

---

## Setup and Usage

### Prerequisites

The following tools are required:

- Python
- Java
- PySpark
- Hadoop Windows utilities
- AWS CLI
- Terraform
- Snowflake
- Sphinx

### 1. Activate the Python Environment

From PowerShell:

```powershell
.\envwarranty\Scripts\Activate.ps1
```

### 2. Configure Hadoop Windows Utilities

The project uses Hadoop Windows utilities for local PySpark execution.

For the current PowerShell session:

```powershell
$env:HADOOP_HOME = "C:\hadoop-win-utils"
$env:Path += ";C:\hadoop-win-utils\bin"

$pythonPath = (Get-Command python).Source
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
```

Verify `winutils.exe`:

```powershell
where.exe winutils
```

### 3. Test Spark

Run:

```powershell
python .\src\processing\test_spark.py
```

### 4. Upload Raw Data

Upload the source CSV files to Amazon S3:

```powershell
aws s3 cp ".\data\sample\warranty_claims.csv" "s3://bmw-warranty-claims-532404260630/raw/warranty/warranty_claims.csv"

aws s3 cp ".\data\sample\vehicle_master.csv" "s3://bmw-warranty-claims-532404260630/raw/vehicle_master/vehicle_master.csv"
```

### 5. Run the Validation Pipeline

```powershell
python .\src\processing\validate_warranty.py
```

### 6. Run Automated Tests

```powershell
python -m pytest .\tests -v
```

### 7. Build Sphinx Documentation

```powershell
sphinx-build -b html docs/source docs/build/html
```

---

## Results

The completed pipeline demonstrates an end-to-end warranty analytics workflow.

The system:

- Ingests warranty and vehicle data
- Stores raw data in Amazon S3
- Validates data using PySpark
- Separates valid and rejected records
- Enriches valid warranty claims
- Stores processed data as Parquet
- Catalogs data using AWS Glue
- Queries data using Amazon Athena
- Loads data into Snowflake
- Performs SQL-based warranty cost analysis
- Provides interactive dashboards using Amazon QuickSight
- Validates processing logic using automated tests
- Provides technical documentation using Sphinx

---

## Key Deliverables

The project delivers the following components:

| Deliverable | Technology |
|---|---|
| Cloud infrastructure | Terraform |
| Raw data storage | Amazon S3 |
| Data validation | PySpark |
| Data transformation | PySpark |
| Metadata catalog | AWS Glue |
| SQL analytics | Amazon Athena |
| Data warehouse | Snowflake |
| Business intelligence | Amazon QuickSight |
| Automated testing | pytest |
| Technical documentation | Sphinx |

---

## Conclusion

This project demonstrates a complete cloud-based data engineering and analytics pipeline for BMW warranty claims.

It combines Infrastructure as Code, distributed data processing, cloud storage, serverless SQL, data warehousing, business intelligence, automated testing, and technical documentation into a single workflow.

The resulting pipeline provides a structured approach for transforming raw warranty data into validated, enriched, and analytically useful information.