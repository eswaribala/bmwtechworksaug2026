# BMW Data Quality & Governance Platform

**Participant 12 — BMW Connected Mobility Data & AI Platform**

> A production-style data quality and governance solution for validating BMW datasets, identifying data-quality issues, quarantining bad records, and generating a measurable **Data Quality Score (0–100)**.

---

## 1. Project Overview

Modern BMW systems generate data from multiple sources such as:

- Connected vehicles
- Vehicle telemetry
- Sales systems
- Dealers
- Maintenance systems
- Warranty systems
- Charging sessions
- Customer feedback

These datasets can contain:

- Missing values
- Duplicate records
- Invalid vehicle IDs
- Invalid VINs
- Invalid dates
- Out-of-range values
- Referential-integrity violations

The purpose of this project is to build a centralized **BMW Data Quality & Governance Platform** that automatically validates incoming data before it is consumed by downstream analytical systems.

The platform separates valid and invalid data, calculates a **Data Quality Score**, generates a quality report, and provides operational visibility through CloudWatch.

---

# 2. Business Problem

BMW data engineers need visibility into the quality of incoming datasets.

Poor-quality data can lead to:

- Incorrect analytics
- Incorrect business KPIs
- Invalid reports
- Faulty downstream processing
- Unreliable dashboards
- Incorrect vehicle information
- Data inconsistencies between systems

Therefore, the platform must answer:

> **"Can BMW trust this dataset for downstream analytics?"**

The solution provides a measurable answer through a **Data Quality Score from 0–100**.

---

# 3. Project Objectives

The system should:

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

---

# 4. Technology Stack

| Layer | Technology |
|---|---|
| Programming | Python |
| Distributed Processing | PySpark |
| Cloud Storage | Amazon S3 |
| Data Catalog | AWS Glue Data Catalog |
| Governance | AWS Lake Formation |
| Analytics | Amazon Athena |
| Monitoring | Amazon CloudWatch |
| Testing | Pytest |
| Version Control | Git / GitHub |
| CI/CD | GitHub Actions |
| Data Format | CSV / Parquet |

The official Participant 12 technology recommendation is **Python/PySpark + Glue Catalog + Lake Formation + CloudWatch**. 

---

# 5. High-Level Architecture

```text
                         BMW DATA SOURCES
                              |
                              v
                    +---------------------+
                    |   Incoming Dataset  |
                    | CSV / JSON / etc.   |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |     Amazon S3       |
                    |      RAW Zone       |
                    +----------+----------+
                               |
                               v
                    +---------------------+
                    |   PySpark Engine    |
                    | Data Processing &    |
                    | Quality Validation  |
                    +----------+----------+
                               |
                +--------------+--------------+
                |                             |
                v                             v
       +------------------+          +------------------+
       |   VALID DATA     |          |   INVALID DATA   |
       |                  |          |                  |
       | Curated Zone     |          | Quarantine Zone  |
       +--------+---------+          +------------------+
                |                             |
                |                             |
                v                             v
       +------------------+          +------------------+
       | AWS Glue Catalog |          | Rejected Records |
       +--------+---------+          +------------------+
                |
                v
       +------------------+
       |  Amazon Athena   |
       | Analytical Query |
       +--------+---------+
                |
                v
       +------------------+
       | Quality Report   |
       | Score 0–100      |
       +------------------+

                +-------------------------+
                |    AWS CloudWatch       |
                | Logs / Metrics / Errors |
                +-------------------------+

                +-------------------------+
                |    AWS Lake Formation   |
                | Data Access Governance  |
                +-------------------------+
```

---

# 6. Detailed Architecture

## 6.1 Data Source Layer

The system receives BMW-style datasets.

Example datasets:

```text
Vehicle Master
Vehicle Telemetry
```

For this project, datasets can be provided as CSV files.

Example:

```text
vehicle_master.csv
telemetry.csv
```

---

# 7. Amazon S3 Data Lake

Amazon S3 acts as the central storage layer.

Recommended structure:

```text
bmw-data-quality/
│
├── raw/
│   ├── vehicle_master/
│   ├── telemetry/
│  
│  
│  
│
│
│
├── processed/
│
├── curated/
│
├── quarantine/
│
├── reports/
│
└── logs/
```

### Raw

Contains the original incoming datasets.

```text
raw/
```

No transformation should be performed directly on the original data.

### Processed

Contains cleaned/transformed intermediate data.

```text
processed/
```

### Curated

Contains validated data ready for analytical consumption.

```text
curated/
```

### Quarantine

Contains records that failed validation.

```text
quarantine/
```

### Reports

Contains generated quality reports.

```text
reports/
```

---

# 8. Data Quality Engine

The core of the project is the **Data Quality Engine**.

The engine receives a dataset and executes a sequence of validation rules.

```text
Input Dataset
     |
     v
Schema Validation
     |
     v
Null Check
     |
     v
Duplicate Check
     |
     v
VIN Validation
     |
     v
Date Validation
     |
     v
Range Validation
     |
     v
Referential Integrity
     |
     v
Quality Score
     |
     +------------+
     |            |
     v            v
 Valid         Invalid
 Records       Records
     |            |
     v            v
 Curated      Quarantine
```

---

# 9. Data Quality Checks

## 9.1 Null Percentage

Identify missing values in important columns.

Example:

```text
vehicle_id
VIN
timestamp
model
region
```

Example result:

```text
vehicle_id null percentage = 0.2%
VIN null percentage        = 0.0%
model null percentage      = 1.4%
```

---

## 9.2 Duplicate Detection

Identify duplicate records.

Example:

```text
event_id
vehicle_id + timestamp
sale_id
claim_id
```

Example:

```text
Total Records       : 10,000
Duplicate Records   : 150
```

Duplicate records should be separated from accepted data.

---

# 10. VIN Validation

The system should identify invalid VIN values.

Example validation requirements:

```text
VIN must:
- Exist
- Have the expected format
- Not contain invalid characters
```

Example:

```text
Valid VIN      → Accepted
Invalid VIN    → Quarantine
Missing VIN    → Quarantine
```

---

# 11. Date Validation

The system should detect invalid dates.

Examples:

```text
2026-01-15        → Valid
2026-15-40        → Invalid
abc               → Invalid
NULL              → Invalid
```

Relevant date fields may include:

```text
sale_date
service_date
claim_date
timestamp
```

---

# 12. Out-of-Range Validation

Business values must be checked against configurable limits.

Example:

```text
battery_level:
0 <= value <= 100

temperature:
configured minimum <= value <= configured maximum

rating:
1 <= value <= 5
```

The exact business thresholds should be maintained in configuration rather than hard-coded wherever possible.

---

# 13. Referential Integrity

The system should verify relationships between datasets.

Example:

```text
Telemetry.vehicle_id
        |
        v
Vehicle_Master.vehicle_id
```

If a telemetry record contains:

```text
vehicle_id = BMW999999
```

but that vehicle does not exist in the vehicle master:

```text
Result → Referential Integrity Failure
```

The record should be rejected or quarantined.

---

# 14. Data Quality Score

The platform generates a score between:

```text
0 – 100
```

Example scoring model:

```text
Data Quality Score =
100
- Null Penalty
- Duplicate Penalty
- Invalid VIN Penalty
- Invalid Date Penalty
- Range Violation Penalty
- Referential Integrity Penalty
```

A configurable weighted scoring model can be implemented.

Example:

| Quality Check | Weight |
|---|---:|
| Null values | 20 |
| Duplicates | 15 |
| Invalid VIN | 20 |
| Invalid dates | 15 |
| Out-of-range values | 15 |
| Referential integrity | 15 |
| **Total** | **100** |

The implementation should document the final scoring formula used.

---

# 15. Example Quality Report

```text
==================================================
          BMW DATA QUALITY REPORT
==================================================

Dataset              : Vehicle Telemetry
Execution Time       : 2026-09-15 10:30:00

--------------------------------------------------
RECORD SUMMARY
--------------------------------------------------

Total Records        : 10,000
Valid Records        : 9,420
Rejected Records     : 580

--------------------------------------------------
QUALITY CHECKS
--------------------------------------------------

Null Records         : 210
Duplicate Records    : 150
Invalid VIN          : 80
Invalid Dates        : 60
Range Violations     : 50
Referential Errors   : 30

--------------------------------------------------
QUALITY SCORE
--------------------------------------------------

Data Quality Score   : 94.2 / 100

Status               : GOOD

==================================================
```

---

# 16. Quality Status

A simple interpretation can be used:

```text
90 – 100  → Excellent
80 – 89   → Good
70 – 79   → Acceptable
50 – 69   → Poor
0 – 49    → Critical
```

These thresholds should be treated as project configuration and can be changed according to business requirements.

---

# 17. Quarantine Process

Invalid records must not simply be deleted.

They should be preserved in the quarantine layer.

```text
                 Input
                   |
                   v
             Validation
                   |
          +--------+--------+
          |                 |
       Valid              Invalid
          |                 |
          v                 v
      Curated            Quarantine
       S3                   S3
          |                 |
          v                 v
      Analytics        Investigation
```

Each quarantined record should ideally contain:

```text
original_record
error_type
error_message
validation_rule
processed_timestamp
dataset_name
```

Example:

```json
{
  "vehicle_id": "BMW999",
  "temperature": 250,
  "error_type": "OUT_OF_RANGE",
  "error_message": "Temperature exceeds allowed range",
  "validation_rule": "temperature_range",
  "dataset": "telemetry"
}
```

---

# 18. AWS Glue Data Catalog

AWS Glue Data Catalog provides metadata for the curated datasets.

Example:

```text
Glue Catalog
     |
     +── bmw_vehicle_master
     |
     +── bmw_telemetry
     |
     +── bmw_sales
     |
     +── bmw_maintenance
     |
     +── bmw_warranty
```

This allows analytical tools such as Athena to discover and query the curated data.

---

# 19. Amazon Athena

Amazon Athena is used to query the curated datasets.

Example:

```sql
SELECT
    model,
    COUNT(*) AS vehicle_count
FROM bmw_vehicle_master
GROUP BY model;
```

Example quality query:

```sql
SELECT
    dataset_name,
    quality_score,
    rejected_records,
    execution_timestamp
FROM data_quality_reports
ORDER BY execution_timestamp DESC;
```

---

# 20. AWS Lake Formation

AWS Lake Formation provides the governance layer.

It can be used to control access to:

```text
Raw Data
Curated Data
Quarantine Data
Quality Reports
```

Example conceptual access model:

```text
Data Engineer
    |
    +--> Raw
    +--> Curated
    +--> Quarantine

Data Analyst
    |
    +--> Curated
    +--> Quality Reports

Business User
    |
    +--> Approved Analytical Data
```

The exact permissions should follow the AWS environment provided for the capstone.

---

# 21. CloudWatch Monitoring

CloudWatch provides operational visibility.

The system should log:

```text
Pipeline Started
Pipeline Completed
Records Processed
Records Accepted
Records Rejected
Quality Score
Validation Errors
Processing Duration
Application Exceptions
```

Example:

```text
[INFO] Pipeline started
[INFO] Dataset: telemetry
[INFO] Records received: 10000
[INFO] Records processed: 10000
[INFO] Valid records: 9420
[WARN] Rejected records: 580
[INFO] Quality score: 94.2
[INFO] Pipeline completed
```

---

# 22. Monitoring Flow

```text
Python / PySpark
       |
       v
Application Logs
       |
       v
CloudWatch Logs
       |
       +----> Errors
       |
       +----> Processing Count
       |
       +----> Execution Time
       |
       +----> Validation Failures
```

---

# 23. Project Folder Structure

Recommended repository structure:

```text
bmw-data-quality-platform/
│
├── README.md
│
├── docs/
│   ├── PRD.md
│   ├── architecture.png
│   ├── data_dictionary.md
│   └── data_quality_rules.md
│
├── data/
│   └── sample/
│       ├── vehicle_master.csv
│       ├── telemetry.csv
│       ├── sales.csv
│       └── maintenance.csv
│
├── src/
│   ├── ingestion/
│   │   └── s3_loader.py
│   │
│   ├── processing/
│   │   ├── data_cleaner.py
│   │   ├── validator.py
│   │   ├── quality_engine.py
│   │   └── quarantine.py
│   │
│   ├── scoring/
│   │   └── quality_score.py
│   │
│   ├── reporting/
│   │   └── quality_report.py
│   │
│   ├── monitoring/
│   │   └── cloudwatch_logger.py
│   │
│   └── utils/
│       ├── config.py
│       └── logger.py
│
├── sql/
│   ├── create_tables.sql
│   ├── quality_queries.sql
│   └── analytics_queries.sql
│
├── tests/
│   ├── test_validator.py
│   ├── test_duplicates.py
│   ├── test_vin.py
│   ├── test_dates.py
│   ├── test_ranges.py
│   └── test_quality_score.py
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── iam.tf
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── requirements.txt
├── .gitignore
└── Dockerfile
```

---

# 24. Processing Workflow

The complete processing flow is:

```text
1. Receive Dataset
       ↓
2. Upload to S3 Raw
       ↓
3. Read Dataset
       ↓
4. Validate Schema
       ↓
5. Run Quality Checks
       ↓
6. Calculate Quality Metrics
       ↓
7. Separate Valid/Invalid Records
       ↓
8. Write Valid Data to Curated S3
       ↓
9. Write Invalid Data to Quarantine S3
       ↓
10. Generate Quality Report
       ↓
11. Register/Update Glue Catalog
       ↓
12. Query using Athena
       ↓
13. Send Logs/Metrics to CloudWatch
```

---

# 25. Example Data Flow

```text
telemetry.csv
     |
     v
S3/raw/telemetry/
     |
     v
PySpark
     |
     +-----------------------------+
     |                             |
     v                             v
Quality Validation           Error Detection
     |                             |
     v                             v
Valid Records                Invalid Records
     |                             |
     v                             v
S3/curated/                  S3/quarantine/
     |                             |
     v                             v
Glue Catalog                 Quality Report
     |
     v
Athena
```

---

# 26. Configuration

Validation rules should be configurable.

Example:

```yaml
quality_rules:

  battery_level:
    min: 0
    max: 100

  temperature:
    min: -40
    max: 120

  rating:
    min: 1
    max: 5

  quality_score:
    excellent: 90
    good: 80
    acceptable: 70
    poor: 50
```

This makes the system easier to modify without changing the core processing code.

---

# 27. Error Handling

The application must handle failures gracefully.

Possible failures:

```text
S3 unavailable
Invalid input file
Missing columns
Incorrect data type
PySpark processing failure
Glue Catalog failure
Athena query failure
Permission error
Unexpected application exception
```

Example:

```text
try
 |
 v
Process Dataset
 |
 +---- Success → Curated
 |
 +---- Failure → Log Error
                  |
                  v
              CloudWatch
```

---

# 28. Automated Testing

At least five automated tests should be implemented.

Recommended tests:

### Test 1 — Null Detection

```text
Input:
vehicle_id = NULL

Expected:
NULL validation failure
```

### Test 2 — Duplicate Detection

```text
Input:
Same event_id appears twice

Expected:
Duplicate detected
```

### Test 3 — VIN Validation

```text
Input:
Invalid VIN

Expected:
VIN validation failure
```

### Test 4 — Date Validation

```text
Input:
Invalid date

Expected:
Date validation failure
```

### Test 5 — Range Validation

```text
Input:
battery_level = 150

Expected:
Out-of-range failure
```

### Test 6 — Quality Score

```text
Input:
Known validation results

Expected:
Correct score
```

---

# 29. CI/CD

GitHub Actions should automatically validate code changes.

Recommended pipeline:

```text
Developer Push
      |
      v
GitHub Actions
      |
      v
Install Dependencies
      |
      v
Lint
      |
      v
Run Pytest
      |
      v
Build
      |
      v
Validation Successful
```

Example repository workflow:

```text
feature branch
      |
      v
commit
      |
      v
pull request
      |
      v
GitHub Actions
      |
      v
Tests
      |
      v
Peer Review
      |
      v
Merge
```

---

# 30. Security Requirements

The project must follow basic security practices.

### Never commit:

```text
AWS Access Keys
AWS Secret Keys
Passwords
API Keys
Tokens
Private credentials
```

Use:

```text
Environment Variables
AWS IAM Roles
AWS Secrets Manager
```

where applicable.

S3 access should follow least-privilege principles.

---

# 31. Sample Environment Configuration

```text
AWS_REGION=
S3_BUCKET=
RAW_PREFIX=
CURATED_PREFIX=
QUARANTINE_PREFIX=
REPORT_PREFIX=
```

Do not commit the actual values containing credentials.

---

# 32. Definition of Done

The project is complete when:

- [ ] Business problem is documented
- [ ] Source data is identified
- [ ] Architecture is documented
- [ ] Raw data is stored in S3
- [ ] Data validation is implemented
- [ ] Processing logic is implemented
- [ ] Valid data is stored in curated zone
- [ ] Invalid data is quarantined
- [ ] Quality score is generated
- [ ] Quality report is generated
- [ ] Glue Catalog is configured
- [ ] Athena can query curated data
- [ ] CloudWatch logging is implemented
- [ ] At least five automated tests pass
- [ ] Exception handling is implemented
- [ ] Credentials are secured
- [ ] README is reproducible
- [ ] Business KPI is demonstrated
- [ ] Final demonstration works

The capstone definition of done specifically requires documented business problem, source, architecture, validation, processing, analytical output, tests, error handling, logs, secured credentials, reproducible README instructions, KPI demonstration, and a working final demo.

---

# 33. Acceptance Criteria

The Participant 12 solution must satisfy:

### AC-01 — Data Validation

The system identifies:

```text
Missing values
Duplicate records
Invalid VIN
Invalid dates
Out-of-range values
Referential integrity issues
```

### AC-02 — Quarantine

Invalid records are separated from valid records.

```text
Valid   → Curated
Invalid → Quarantine
```

### AC-03 — Quality Score

The system produces:

```text
Data Quality Score: 0–100
```

### AC-04 — Quality Report

A report containing validation results is generated.

### AC-05 — Analytical Access

Curated data is registered in Glue Catalog and can be queried through Athena.

### AC-06 — Monitoring

Pipeline execution and failures are logged through CloudWatch.

### AC-07 — Testing

Major validation rules have automated tests.

---

# 34. Example Final Demonstration

During the final presentation, demonstrate the following scenario.

### Step 1 — Upload Dataset

```text
telemetry.csv
       ↓
S3/raw/telemetry/
```

### Step 2 — Start Processing

```text
PySpark Data Quality Engine
```

### Step 3 — Show Validation

```text
Total Records       : 10,000
Valid Records       : 9,420
Rejected Records    : 580
```

### Step 4 — Show Issues

```text
Nulls              : 210
Duplicates         : 150
Invalid VIN        : 80
Invalid Dates      : 60
Range Violations   : 50
Referential Errors : 30
```

### Step 5 — Show Quarantine

```text
S3/quarantine/
```

Open a rejected record and explain why it failed.

### Step 6 — Show Curated Data

```text
S3/curated/
```

### Step 7 — Show Athena

Execute an analytical SQL query.

### Step 8 — Show Quality Score

```text
DATA QUALITY SCORE

       94.2 / 100

          GOOD
```

### Step 9 — Show CloudWatch

Demonstrate:

```text
Records Processed
Processing Time
Validation Errors
Pipeline Status
```

### Step 10 — Demonstrate Failure Recovery

Introduce an invalid dataset and show:

```text
Invalid Input
     ↓
Validation Failure
     ↓
Error Logged
     ↓
Bad Data Quarantined
     ↓
Pipeline Continues / Fails Safely
```

---

# 35. Five-Day Development Plan

## Day 1 — Business Understanding & Architecture

### Tasks

- Understand business problem
- Define personas
- Define KPIs
- Define data-quality rules
- Create PRD
- Create architecture diagram
- Create data dictionary
- Create Git repository
- Create S3 structure
- Prepare sample dataset

### Deliverables

```text
PRD
Architecture
Data Dictionary
Data Quality Rules
Git Repository
S3 Structure
```

---

## Day 2 — Data Engineering

### Tasks

- Upload datasets
- Read datasets
- Implement PySpark processing
- Implement null validation
- Implement duplicate validation
- Implement VIN validation
- Implement date validation
- Implement range validation
- Implement referential integrity

### Deliverables

```text
Working ETL
PySpark Code
Validation Engine
Processed Data
Unit Tests
```

---

## Day 3 — Business Feature

### Tasks

- Implement quality score
- Implement quarantine
- Generate quality report
- Configure Glue Catalog
- Configure Athena
- Add CloudWatch logging

### Deliverables

```text
Quality Score
Quality Report
Curated Dataset
Quarantine Dataset
Athena Queries
CloudWatch Logs
```

---

## Day 4 — Production Engineering

### Tasks

- Add automated tests
- Add error handling
- Add logging
- Create Git branches
- Create pull request
- Peer review
- Configure GitHub Actions
- Security validation
- Optional Terraform

### Deliverables

```text
Tests
CI/CD
Monitoring
Security Checklist
Deployment Instructions
```

---

## Day 5 — UAT & Final Demo

### Test:

```text
Happy Path
Invalid Input
Missing Data
Duplicate Data
Invalid VIN
Invalid Date
Out-of-Range Data
Service Failure
Recovery
```

### Final Deliverables

```text
README
PRD
Architecture
Data Model
Testing Report
Deployment Steps
Known Limitations
Future Enhancements
```

---

# 36. Future Enhancements

After the MVP is stable, the following can be considered:

```text
Real-time data-quality validation
Kafka integration
Advanced data lineage
Automated data-quality alerts
Machine learning anomaly detection
Advanced Lake Formation governance
React dashboard
QuickSight dashboard
Terraform infrastructure
Advanced CloudWatch alarms
```

These should be treated as **stretch goals**, not prerequisites for the five-day MVP.

---

# 37. Project Success Criteria

The project is successful when a data engineer can:

```text
Upload BMW data
      ↓
Run validation
      ↓
Identify bad data
      ↓
Quarantine bad records
      ↓
View quality metrics
      ↓
Understand the quality score
      ↓
Query trusted data
      ↓
Monitor the pipeline
```

The core success condition from the capstone is that **bad data is quarantined and a quality report is produced**.

---

# 38. Final Architecture Summary

```text
                         ┌──────────────────────┐
                         │    BMW DATA SOURCES  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      AMAZON S3       │
                         │       RAW ZONE       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       PYSPARK        │
                         │  DATA QUALITY ENGINE │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     │                             │
                     ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │   VALID DATA     │          │   INVALID DATA   │
          │                  │          │                  │
          │ CURATED S3       │          │ QUARANTINE S3   │
          └────────┬─────────┘          └──────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │  GLUE CATALOG    │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │     ATHENA       │
          │ ANALYTICAL QUERY │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ QUALITY REPORT   │
          │   SCORE 0–100    │
          └──────────────────┘

        ┌─────────────────────────────────────┐
        │           GOVERNANCE                │
        │          LAKE FORMATION             │
        └─────────────────────────────────────┘

        ┌─────────────────────────────────────┐
        │           OBSERVABILITY             │
        │             CLOUDWATCH              │
        │ Logs • Metrics • Errors • Alerts    │
        └─────────────────────────────────────┘
```

---

## 39. One-Line Project Description

> **BMW Data Quality & Governance Platform is a PySpark-based AWS data-quality solution that validates BMW datasets, quarantines bad records, generates a 0–100 data-quality score, and provides governed, observable analytical data through S3, Glue, Athena, Lake Formation, and CloudWatch.**

---

## 40. Participant Ownership

**Participant:** 12  
**Use Case:** BMW Data Quality & Governance Platform  
**Pod:** Pod D — Data Engineering & Streaming  
**Primary Technologies:** Python, PySpark, AWS S3, Glue Catalog, Lake Formation, CloudWatch  
**Primary Output:** Data Quality Score + Quality Report + Curated/Quarantined Data

The capstone assigns Participant 12 specifically to the **Data Quality & Governance Platform**, under Pod D, with individual ownership of the deliverable.