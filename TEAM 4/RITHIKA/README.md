# BMW Snowflake Incremental Data Warehouse

## 1. Project Overview

This project implements an incremental BMW data warehouse using **Python, AWS S3, Terraform, Snowflake SQL, Streams, Tasks, Stored Procedures, Fact/Dimension modelling, Time Travel and Zero-Copy Cloning**.

The objective is to build an end-to-end data platform in which BMW telemetry, sales, vehicle and dealer data are validated, stored in Amazon S3, loaded into Snowflake, transformed through layered warehouse structures, and processed incrementally into analytical fact and dimension tables.

The project supports both:

- Initial/batch loading of source files
- Incremental loading of new source files
- Historical data access using Snowflake Time Travel
- Development/testing using Zero-Copy Cloning
- Infrastructure provisioning using Terraform

---

## 2. Project Objectives

The project was designed to demonstrate:

- AWS S3 as a cloud data landing zone
- Terraform-based AWS infrastructure provisioning
- Python-based source validation and S3 ingestion
- Snowflake External Stage integration with S3
- RAW and STAGING data layers
- Dimensional data modelling
- Fact tables and dimension tables
- Snowflake Streams for incremental change capture
- Snowflake Tasks for orchestration
- Stored Procedures for transformation and MERGE processing
- Incremental propagation of newly arrived source files
- Data quality checks
- Snowflake Time Travel
- Snowflake Zero-Copy Cloning
- Business-oriented analytical queries

---

## 3. Architecture

```text
                    BMW SOURCE DATA
                          |
                          v
                +--------------------+
                | Python Ingestion   |
                |--------------------|
                | CSV validation     |
                | Data quality       |
                | S3 upload          |
                +---------+----------+
                          |
                          v
                +--------------------+
                | AWS S3 Bucket      |
                |--------------------|
                | raw/telemetry/     |
                | raw/sales/         |
                | raw/vehicle/       |
                | raw/dealer/        |
                +---------+----------+
                          |
                          v
              +-------------------------+
              | Snowflake External      |
              | Stage                   |
              +------------+------------+
                           |
                           v
                +--------------------+
                | RAW Layer          |
                |--------------------|
                | RAW_TELEMETRY      |
                | RAW_SALES          |
                | RAW_VEHICLE        |
                | RAW_DEALER         |
                +---------+----------+
                          |
                          v
                +--------------------+
                | STAGING Layer      |
                |--------------------|
                | STG_TELEMETRY      |
                | STG_SALES          |
                | STG_VEHICLE        |
                | STG_DEALER         |
                +---------+----------+
                          |
                    Streams / Tasks
                          |
                          v
                +--------------------+
                | Stored Procedures  |
                | Incremental MERGE  |
                +---------+----------+
                          |
                          v
               +----------------------+
               | ANALYTICS Layer      |
               |----------------------|
               | DIM_VEHICLE          |
               | DIM_DEALER           |
               | DIM_REGION           |
               | DIM_DATE             |
               | FACT_TELEMETRY       |
               | FACT_SALES           |
               +----------+-----------+
                          |
                          v
                   Analytics Queries
```

---

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Source validation and S3 ingestion |
| Pandas | CSV loading and validation |
| PySpark | Telemetry processing where applicable |
| AWS S3 | Cloud data landing zone |
| Terraform | AWS infrastructure provisioning |
| AWS IAM | Role and S3 access management |
| AWS CloudWatch | Infrastructure logging |
| Snowflake | Data warehouse and analytical processing |
| Snowflake External Stage | Access to files stored in S3 |
| Snowflake Streams | Change capture for incremental processing |
| Snowflake Tasks | Automated processing |
| Snowflake Stored Procedures | Transformation and MERGE logic |
| SQL | Warehouse modelling and analytics |

---

## 5. Repository Structure

```text
RITHIKA/
|
+-- data/
|   +-- telemetry/
|   |   +-- telemetry_initial.csv
|   |   +-- telemetry_incremental.csv
|   +-- sales/
|   |   +-- sales_initial.csv
|   |   +-- sales_incremental.csv
|   +-- vehicle/
|   |   +-- vehicle_master.csv
|   +-- dealer/
|       +-- dealer_master.csv
|
+-- python/
|   +-- __init__.py
|   +-- config.py
|   +-- logger.py
|   +-- s3_ingestion.py
|   +-- data_validation.py
|   +-- main.py
|
+-- pyspark/
|   +-- __init__.py
|   +-- telemetry_processing.py
|
+-- snowflake/
|   +-- 01_database.sql
|   +-- 02_file_formats.sql
|   +-- 03_stages.sql
|   +-- 04_raw_tables.sql
|   +-- 05_staging_tables.sql
|   +-- 06_dimensions.sql
|   +-- 07_fact_tables.sql
|   +-- 08_streams.sql
|   +-- 09_procedures.sql
|   +-- 10_tasks.sql
|   +-- 11_initial_load.sql
|   +-- 12_time_travel.sql
|   +-- 13_zero_copy_clone.sql
|   +-- 14_analytics.sql
|
+-- terraform/
|   +-- main.tf
|   +-- variables.tf
|   +-- iam.tf
|   +-- outputs.tf
|
+-- tests/
|   +-- __init__.py
|   +-- test_validation.py
|   +-- test_transformation.py
|   +-- test_data_quality.py
|   +-- test_incremental.py
|   +-- test_config.py
|
+-- docs/
+-- pyproject.toml
+-- .env.example
+-- README.md
```

---

## 6. Source Data

The project uses four source datasets.

### Telemetry

Vehicle telemetry contains sensor and location information such as event ID, vehicle ID, timestamp, speed, battery, temperature and location-related attributes.

Files:

```text
data/telemetry/telemetry_initial.csv
data/telemetry/telemetry_incremental.csv
```

### Sales

Sales contains transaction attributes such as:

```text
sales_id
customer_id
vehicle_id
dealer_id
purchase_date
sale_price
quantity
```

Files:

```text
data/sales/sales_initial.csv
data/sales/sales_incremental.csv
```

### Vehicle Master

Vehicle reference data includes:

```text
vehicle_id
model
make
fuel_type
vehicle_year
segment
```

File:

```text
data/vehicle/vehicle_master.csv
```

### Dealer Master

Dealer reference data contains dealer-related attributes used by the analytical model.

File:

```text
data/dealer/dealer_master.csv
```

---

## 7. AWS S3 Landing Layer

Amazon S3 is used as the cloud landing zone for source data.

Files are organized under the `raw` prefix:

```text
raw/
+-- telemetry/
+-- sales/
+-- vehicle/
+-- dealer/
```

Example objects:

```text
raw/telemetry/telemetry_initial.csv
raw/telemetry/telemetry_incremental.csv
raw/sales/sales_initial.csv
raw/sales/sales_incremental.csv
raw/vehicle/vehicle_master.csv
raw/dealer/dealer_master.csv
```

The initial and incremental files are kept separately so that the incremental pipeline can be demonstrated after the initial warehouse load.

---

## 8. Terraform Infrastructure

Terraform is used to provision and manage the AWS infrastructure for the project.

The infrastructure includes:

- S3 bucket
- S3 versioning
- S3 encryption
- S3 public access blocking
- IAM policy
- IAM role used for Snowflake access
- IAM role-policy attachment
- CloudWatch log group

### Terraform workflow

```text
Terraform configuration
        |
        v
terraform init
        |
        v
terraform validate
        |
        v
terraform plan
        |
        v
terraform apply
        |
        v
AWS infrastructure
```

### Initialize Terraform

```powershell
cd terraform
terraform init
```

### Validate

```powershell
terraform validate
```

### Review changes

```powershell
terraform plan
```

### Apply

```powershell
terraform apply
```

The Terraform plan should be reviewed before applying changes to existing infrastructure.

---

## 9. IAM and Snowflake Access

An AWS IAM role is used by the Snowflake storage integration to access the S3 bucket.

The conceptual authorization flow is:

```text
Snowflake
    |
    | sts:AssumeRole
    v
AWS IAM Role
    |
    | S3 permissions
    v
BMW S3 Bucket
```

The IAM role's trust policy identifies the Snowflake-provided AWS principal and uses the Snowflake external ID. The attached permissions policy grants the role the S3 permissions needed for the warehouse to read the landing files.

The role and policy are infrastructure resources managed through Terraform where applicable.

---

## 10. Python Ingestion Layer

Python is responsible for source validation and uploading data files to S3.

The main entry point is:

```text
python/main.py
```

Supported ingestion types:

```text
telemetry
sales
vehicle
dealer
```

Examples:

```powershell
python -m python.main --type telemetry --file data/telemetry/telemetry_initial.csv
```

```powershell
python -m python.main --type sales --file data/sales/sales_initial.csv
```

```powershell
python -m python.main --type vehicle --file data/vehicle/vehicle_master.csv
```

```powershell
python -m python.main --type dealer --file data/dealer/dealer_master.csv
```

For telemetry and sales, validation is performed before the files are uploaded to S3.

The Python layer therefore acts as the controlled ingestion boundary between local source files and the cloud landing zone.

---

## 11. Snowflake Warehouse Layers

The Snowflake database is divided into three logical layers:

```text
RAW
STAGING
ANALYTICS
```

### RAW layer

The RAW layer contains the first Snowflake copy of the source data loaded from S3.

Tables:

```text
RAW_TELEMETRY
RAW_SALES
RAW_VEHICLE
RAW_DEALER
```

### STAGING layer

The STAGING layer is the intermediate processing layer.

Tables:

```text
STG_TELEMETRY
STG_SALES
STG_VEHICLE
STG_DEALER
```

### ANALYTICS layer

The ANALYTICS layer contains the dimensional warehouse model.

Dimensions:

```text
DIM_VEHICLE
DIM_DEALER
DIM_REGION
DIM_DATE
```

Facts:

```text
FACT_TELEMETRY
FACT_SALES
```

---

## 12. Snowflake External Stage

The Snowflake external stage is the bridge between the S3 landing zone and the RAW layer.

The flow is:

```text
S3 bucket
   |
   v
Storage Integration
   |
   v
External Stage
   |
   v
COPY INTO
   |
   v
RAW tables
```

Example stage definition:

```sql
CREATE OR REPLACE STAGE RAW.BMW_S3_STAGE
URL = 's3://<bucket>/raw/'
STORAGE_INTEGRATION = BMW_S3_INTEGRATION
FILE_FORMAT = CSV_FORMAT;
```

The stage can be inspected with:

```sql
LIST @RAW.BMW_S3_STAGE;
```

The returned file list confirms that Snowflake can see the objects stored in the S3 landing path.

---

## 13. Loading S3 Files into RAW Tables

The source files are loaded from the external stage into Snowflake RAW tables using `COPY INTO`.

Example pattern:

```sql
COPY INTO RAW.RAW_TELEMETRY
FROM @RAW.BMW_S3_STAGE/telemetry/
FILE_FORMAT = (FORMAT_NAME = 'RAW.CSV_FORMAT');
```

Equivalent `COPY INTO` operations are performed for sales, vehicle and dealer data.

Therefore the S3-to-Snowflake flow is:

```text
CSV source
   |
   v
S3 raw/ prefix
   |
   v
Snowflake External Stage
   |
   v
COPY INTO
   |
   v
RAW table
```

This separates cloud storage from warehouse processing while preserving the original source files in S3.

---

## 14. Staging Layer

The STAGING layer is populated from RAW data and acts as the controlled transformation layer before analytical processing.

Initial staging can be populated with SQL such as:

```sql
INSERT INTO STAGING.STG_TELEMETRY
SELECT *
FROM RAW.RAW_TELEMETRY;
```

Similar operations are applied to sales, vehicle and dealer data.

The staging layer provides a stable source for the downstream incremental Stream and MERGE logic.

---

## 15. Dimensional Model

The analytical layer follows a star-schema style model.

### Dimensions

`DIM_VEHICLE` stores vehicle attributes.

`DIM_DEALER` stores dealer information.

`DIM_REGION` stores region reference information.

`DIM_DATE` provides reusable calendar/date attributes.

### Facts

`FACT_TELEMETRY` stores vehicle telemetry events.

`FACT_SALES` stores vehicle sales transactions.

The facts use dimension keys so that business transactions can be analysed using vehicle, dealer, region and date attributes.

---

## 16. Snowflake Streams

Streams are used to capture table changes for incremental processing.

The project uses Streams for the main staging entities:

```text
TELEMETRY_STREAM
SALES_STREAM
VEHICLE_STREAM
DEALER_STREAM
```

Example:

```sql
CREATE OR REPLACE STREAM STAGING.TELEMETRY_STREAM
ON TABLE STAGING.STG_TELEMETRY;
```

The stream provides a change set for downstream processing instead of requiring a full reload of the table.

---

## 17. Incremental Processing

Incremental processing is the core functionality of the project.

The incremental flow is:

```text
New source CSV
      |
      v
Python validation
      |
      v
S3 raw/
      |
      v
Snowflake External Stage
      |
      v
COPY INTO RAW
      |
      v
STAGING changes
      |
      v
Snowflake Stream
      |
      v
Task / Stored Procedure
      |
      v
MERGE
      |
      v
FACT and DIM tables
```

Only new or changed source records are propagated through the incremental path. The initial files establish the baseline, while the incremental files demonstrate subsequent processing.

---

## 18. Stored Procedures

Stored Procedures contain the transformation and incremental merge logic.

The general processing pattern is:

```text
Stream
  |
  v
Read changed records
  |
  v
Transform / enrich
  |
  v
Resolve dimension keys
  |
  v
MERGE into target
```

`MERGE` logic is used so that existing business keys can be updated while previously unseen keys are inserted.

This makes the incremental processing repeatable and prevents duplicate business records when the same source information is encountered again.

---

## 19. Snowflake Tasks

Tasks provide automated execution of the incremental pipeline.

The logical flow is:

```text
Scheduled Task
      |
      v
Check for stream data
      |
      +---- No data ----> End
      |
      +---- Data -------> Stored Procedure
                              |
                              v
                            MERGE
```

The task can be scheduled to run periodically and invoke the incremental processing procedure when change data is available.

---

## 20. Initial Load

The initial load establishes the baseline warehouse state.

```text
telemetry_initial.csv
sales_initial.csv
vehicle_master.csv
dealer_master.csv
          |
          v
         S3
          |
          v
 External Stage
          |
          v
        RAW
          |
          v
      STAGING
          |
          v
   DIMENSIONS + FACTS
```

After the initial load, the warehouse contains the baseline records required to demonstrate incremental processing.

---

## 21. Incremental Load Demonstration

Incremental files are intentionally kept separate from initial files:

```text
data/telemetry/telemetry_incremental.csv
data/sales/sales_incremental.csv
```

They are uploaded to S3 after the initial warehouse state has been established.

The incremental demonstration is:

```text
Initial data
   |
   v
S3 -> Stage -> RAW -> STAGING -> Facts/Dimensions
   |
   | new source files
   v
Incremental data
   |
   v
S3 -> Stage -> RAW -> Streams -> Procedures -> MERGE
   |
   v
Updated analytical tables
```

This demonstrates that new source data is propagated through the existing warehouse without rebuilding the entire analytical layer.

---

## 22. Idempotent Processing

The target loading logic uses business keys and `MERGE` operations to prevent duplicate records.

Conceptually:

```sql
MERGE INTO target t
USING source s
ON t.business_key = s.business_key

WHEN MATCHED THEN
    UPDATE SET ...

WHEN NOT MATCHED THEN
    INSERT (...);
```

This makes repeated pipeline execution safer and supports incremental warehouse maintenance.

---

## 23. Data Quality

Validation is performed at the source and warehouse levels.

Typical checks include:

- required columns
- null values
- duplicate business keys
- invalid numeric values
- timestamp/date validation
- source-file existence
- fact-to-dimension relationships

Example duplicate check:

```sql
SELECT EVENT_ID, COUNT(*)
FROM ANALYTICS.FACT_TELEMETRY
GROUP BY EVENT_ID
HAVING COUNT(*) > 1;
```

Example null check:

```sql
SELECT COUNT(*)
FROM ANALYTICS.FACT_TELEMETRY
WHERE EVENT_ID IS NULL;
```

---

## 24. Time Travel

Snowflake Time Travel is used to query earlier versions of a table.

Example:

```sql
SELECT *
FROM ANALYTICS.FACT_SALES
AT (OFFSET => -60 * 5);
```

This provides a way to inspect the historical state of warehouse data within Snowflake's retention period.

---

## 25. Zero-Copy Clone

A development/test copy of a Snowflake table can be created using cloning.

Example:

```sql
CREATE OR REPLACE TABLE ANALYTICS.FACT_SALES_CLONE
CLONE ANALYTICS.FACT_SALES;
```

The cloned table can then be queried independently:

```sql
SELECT COUNT(*)
FROM ANALYTICS.FACT_SALES_CLONE;
```

This demonstrates the use of Snowflake's zero-copy cloning capability for development or analysis.

---

## 26. Analytics

The analytical model supports queries such as:

### Total revenue

```sql
SELECT
    SUM(SALE_AMOUNT) AS TOTAL_REVENUE,
    COUNT(*) AS TOTAL_SALES,
    AVG(SALE_AMOUNT) AS AVERAGE_SALE_VALUE
FROM ANALYTICS.FACT_SALES;
```

### Revenue by region

```sql
SELECT
    r.REGION_NAME,
    SUM(f.SALE_AMOUNT) AS TOTAL_REVENUE
FROM ANALYTICS.FACT_SALES f
JOIN ANALYTICS.DIM_REGION r
    ON f.REGION_KEY = r.REGION_KEY
GROUP BY r.REGION_NAME;
```

### Telemetry summary

```sql
SELECT
    COUNT(*) AS TOTAL_EVENTS,
    AVG(SPEED_KMH) AS AVG_SPEED,
    AVG(BATTERY_LEVEL) AS AVG_BATTERY_LEVEL,
    AVG(TEMPERATURE_C) AS AVG_TEMPERATURE
FROM ANALYTICS.FACT_TELEMETRY;
```

These outputs demonstrate that the warehouse supports business-facing analysis rather than only raw data storage.

---

## 27. SQL Execution Order

Execute the Snowflake scripts in dependency order:

```text
01_database.sql
       |
       v
02_file_formats.sql
       |
       v
03_stages.sql
       |
       v
04_raw_tables.sql
       |
       v
05_staging_tables.sql
       |
       v
06_dimensions.sql
       |
       v
07_fact_tables.sql
       |
       v
08_streams.sql
       |
       v
09_procedures.sql
       |
       v
10_tasks.sql
       |
       v
11_initial_load.sql
       |
       v
12_time_travel.sql
       |
       v
13_zero_copy_clone.sql
       |
       v
14_analytics.sql
```

This order ensures that all referenced objects exist before dependent objects are created.

---

## 28. Local Setup

### Prerequisites

Install:

- Python 3.10+
- AWS CLI
- Terraform
- Snowflake account
- Git

### Create virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Install the project

```powershell
python -m pip install -e .
```

---

## 29. Environment Variables

Create `.env` from `.env.example`.

Example:

```env
AWS_REGION=eu-north-1
S3_BUCKET=<your-s3-bucket>
S3_RAW_PREFIX=raw
```

Snowflake credentials, when required by a Python component, should also be supplied through environment variables rather than committed to source control.

Never commit:

```text
.env
```

---

## 30. Verification Commands

### AWS S3

```powershell
aws s3 ls s3://<bucket>/raw/ --recursive
```

### Terraform

```powershell
terraform validate
terraform plan
```

### Snowflake stage

```sql
LIST @RAW.BMW_S3_STAGE;
```

### RAW counts

```sql
SELECT COUNT(*) FROM RAW.RAW_TELEMETRY;
SELECT COUNT(*) FROM RAW.RAW_SALES;
SELECT COUNT(*) FROM RAW.RAW_VEHICLE;
SELECT COUNT(*) FROM RAW.RAW_DEALER;
```

### STAGING counts

```sql
SELECT COUNT(*) FROM STAGING.STG_TELEMETRY;
SELECT COUNT(*) FROM STAGING.STG_SALES;
SELECT COUNT(*) FROM STAGING.STG_VEHICLE;
SELECT COUNT(*) FROM STAGING.STG_DEALER;
```

### FACT counts

```sql
SELECT COUNT(*) FROM ANALYTICS.FACT_TELEMETRY;
SELECT COUNT(*) FROM ANALYTICS.FACT_SALES;
```

### Streams

```sql
SHOW STREAMS IN SCHEMA STAGING;
```

### Tasks

```sql
SHOW TASKS IN SCHEMA ANALYTICS;
```

---

## 31. Final Data Flow

The complete implementation can be summarized as:

```text
BMW CSV Files
      |
      v
Python Validation
      |
      v
AWS S3
      |
      v
Snowflake External Stage
      |
      v
COPY INTO
      |
      v
RAW Tables
      |
      v
STAGING Tables
      |
      v
Streams
      |
      v
Tasks
      |
      v
Stored Procedures
      |
      v
MERGE / Incremental Processing
      |
      +----------------------+
      |                      |
      v                      v
Dimension Tables         Fact Tables
      |                      |
      +----------+-----------+
                 |
                 v
             ANALYTICS
```

---

## 32. Project Outcome

The completed project demonstrates an end-to-end BMW data platform in which source files are validated with Python, stored in Amazon S3, accessed through a Snowflake external stage, loaded into RAW tables using `COPY INTO`, transformed through STAGING, and incrementally propagated into analytical fact and dimension tables using Snowflake Streams, Tasks and Stored Procedures.

Terraform provides reproducible AWS infrastructure, while Snowflake features such as Time Travel and Zero-Copy Cloning demonstrate platform-level capabilities beyond basic table creation and querying.

The resulting platform supports both historical/batch processing and incremental ingestion of newly arriving BMW source data.
