# BMW Data Quality & Governance Platform

## Participant 12

A data-quality and governance platform designed to validate BMW datasets, identify data-quality issues, quarantine invalid records, and generate a **Data Quality Score from 0–100**.

---

## 1. Project Overview

BMW systems generate large volumes of data from vehicles and business systems. Before this data is used for analytics, it must be checked for quality and consistency.

This project provides a centralized **Data Quality Engine** that validates incoming BMW datasets and separates trusted data from problematic records.

The platform performs checks for:

- Null values
- Duplicate records
- Referential integrity
- Invalid VINs
- Invalid dates
- Out-of-range values

Invalid records are moved to a **quarantine area**, while valid records are made available for downstream analytics.

---

## 2. Problem Statement

Data coming from different BMW systems may contain incomplete, duplicated, inconsistent, or invalid information.

For example:

```text
Missing vehicle_id
Duplicate telemetry event
Invalid VIN
Invalid date
Battery level = 150%
Unknown vehicle_id
```

If such data is directly consumed by analytical systems, it can produce incorrect business results.

### Business Question

> **"How reliable is the BMW dataset before it is used for analytics?"**

The platform answers this question through a **Data Quality Score between 0 and 100**.

---

# 3. Objectives

The system should:

1. Receive BMW datasets.
2. Store raw data in Amazon S3.
3. Validate the incoming data.
4. Detect data-quality issues.
5. Separate valid and invalid records.
6. Quarantine bad records.
7. Calculate a Data Quality Score.
8. Generate a quality report.
9. Register datasets using AWS Glue Catalog.
10. Provide governed access using Lake Formation.
11. Monitor processing using CloudWatch.

---

# 4. Technology Stack

| Component       | Technology            | Purpose                           |
| --------------- | --------------------- | --------------------------------- |
| Programming     | Python                | Application and validation logic  |
| Processing      | PySpark               | Dataset processing and validation |
| Storage         | Amazon S3             | Raw, curated and quarantine data  |
| Catalog         | AWS Glue Data Catalog | Dataset metadata                  |
| Governance      | AWS Lake Formation    | Data access control               |
| Monitoring      | Amazon CloudWatch     | Logs and operational monitoring   |
| Query           | Amazon Athena         | Query curated data                |
| Testing         | Pytest                | Automated testing                 |
| Version Control | Git / GitHub          | Source-code management            |

The project specification identifies **Python/PySpark + Glue Catalog + Lake Formation + CloudWatch** as the primary technology set for Participant 12.

---

# 5. Architecture

## 5.1 High-Level Architecture

```text
                    BMW DATASET
                         |
                         v
                +----------------+
                |   Amazon S3    |
                |    RAW ZONE    |
                +-------+--------+
                        |
                        v
                +----------------+
                |    PySpark     |
                | Data Quality   |
                |     Engine     |
                +-------+--------+
                        |
              +---------+---------+
              |                   |
              v                   v
       +-------------+     +-------------+
       | VALID DATA  |     | INVALID DATA|
       +------+------+     +------+------+
              |                   |
              v                   v
       +-------------+     +-------------+
       |  CURATED    |     | QUARANTINE  |
       |     S3      |     |     S3      |
       +------+------+     +-------------+
              |
              v
       +-------------+
       | Glue Catalog|
       +------+------+
              |
              v
       +-------------+
       |   Athena    |
       +------+------+
              |
              v
       +-------------+
       |   Quality   |
       |   Report    |
       +-------------+

       +----------------------+
       |    Lake Formation    |
       | Data Governance      |
       +----------------------+

       +----------------------+
       |      CloudWatch      |
       | Logs / Metrics       |
       +----------------------+
```

---

# 6. Detailed Data Flow

```text
BMW Dataset
     |
     v
S3 Raw
     |
     v
Read Dataset using PySpark
     |
     v
Schema Validation
     |
     v
Data Quality Checks
     |
     +-------------------------------+
     |                               |
     v                               v
All Checks Passed              Validation Failed
     |                               |
     v                               v
Curated S3                    Quarantine S3
     |                               |
     v                               v
Glue Catalog                  Error Details
     |
     v
Athena
     |
     v
Analytical Data
```

At the same time:

```text
PySpark Data Quality Engine
          |
          v
      CloudWatch
          |
    +-----+------+
    |            |
   Logs        Metrics
```

---

# 7. S3 Data Lake Structure

Create a dedicated S3 bucket for the project.

Recommended structure:

```text
bmw-data-quality/
│
├── raw/
│   ├── vehicle_master/
│   ├── telemetry/
│   ├── sales/
│   ├── maintenance/
│   ├── warranty/
│   └── charging/
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

Original datasets received from BMW data sources.

```text
s3://bmw-data-quality/raw/
```

### Curated

Validated records that passed the required quality checks.

```text
s3://bmw-data-quality/curated/
```

### Quarantine

Records that failed one or more quality checks.

```text
s3://bmw-data-quality/quarantine/
```

### Reports

Generated data-quality reports.

```text
s3://bmw-data-quality/reports/
```

---

# 8. Data Quality Engine

The Data Quality Engine is the main component of this project.

```text
                Input Dataset
                     |
                     v
             +---------------+
             | Schema Check   |
             +-------+-------+
                     |
                     v
             +---------------+
             |   Null Check   |
             +-------+-------+
                     |
                     v
             +---------------+
             |Duplicate Check |
             +-------+-------+
                     |
                     v
             +---------------+
             |   VIN Check    |
             +-------+-------+
                     |
                     v
             +---------------+
             |   Date Check   |
             +-------+-------+
                     |
                     v
             +---------------+
             |  Range Check   |
             +-------+-------+
                     |
                     v
             +---------------+
             | Referential    |
             |   Integrity    |
             +-------+-------+
                     |
                     v
             Quality Score
                     |
              +------+------+
              |             |
              v             v
           VALID         INVALID
              |             |
              v             v
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

Example output:

```text
Column          Null Count       Null %
-----------------------------------------
vehicle_id         10             0.10%
VIN                 0             0.00%
model              25             0.25%
region              5             0.05%
```

---

# 10. Duplicate Detection

The system identifies duplicate records.

Possible unique identifiers:

```text
event_id
sale_id
service_id
claim_id
```

For telemetry:

```text
vehicle_id + timestamp
```

can also be used depending on the dataset.

Example:

```text
Total Records     : 10,000
Duplicate Records : 150
```

Duplicate records should be identified and handled according to the project's validation rules.

---

# 11. Referential Integrity

The system checks whether records correctly reference related BMW datasets.

Example:

```text
Vehicle Master
      |
      | vehicle_id
      v
Telemetry
```

If:

```text
Telemetry.vehicle_id = BMW12345
```

but:

```text
BMW12345
```

does not exist in the Vehicle Master dataset, the record fails the referential-integrity check.

```text
Vehicle exists     → PASS
Vehicle not found  → FAIL
```

---

# 12. VIN Validation

The system validates VIN values according to the project's defined VIN rules.

Examples of invalid conditions:

```text
VIN is NULL
VIN has incorrect format
VIN contains invalid characters
VIN does not satisfy required length/format
```

Example:

```text
VIN                 Status
--------------------------------
VALID_VIN_VALUE     PASS
INVALID_VALUE       FAIL
NULL                FAIL
```

---

# 13. Date Validation

The system validates date and timestamp fields.

Possible fields:

```text
timestamp
sale_date
service_date
claim_date
```

Example:

```text
2026-09-15        → PASS
2026-15-40        → FAIL
abc               → FAIL
NULL              → FAIL
```

---

# 14. Out-of-Range Validation

The platform identifies values outside the expected business range.

Example:

### Battery Level

```text
0 <= battery_level <= 100
```

Therefore:

```text
85   → PASS
50   → PASS
100  → PASS
150  → FAIL
-10  → FAIL
```

Other business fields can have their own configurable ranges.

---

# 15. Data Quality Score

The platform produces a:

```text
Data Quality Score
       0–100
```

The score represents the overall quality of the processed dataset.

Example:

```text
Total Records       : 10,000
Valid Records       : 9,420
Rejected Records    : 580

Data Quality Score  : 94.2 / 100
```

A configurable scoring mechanism should be implemented based on the number/severity of validation failures.

Example conceptual model:

```text
100
 |
 |---- Null violations
 |
 |---- Duplicate violations
 |
 |---- Invalid VIN
 |
 |---- Invalid dates
 |
 |---- Range violations
 |
 |---- Referential-integrity violations
 |
 v
Final Quality Score
```

---

# 16. Quality Report

The system should generate a quality report after processing.

Example:

```text
==========================================
       BMW DATA QUALITY REPORT
==========================================

Dataset              : Telemetry
Execution Time       : 2026-09-15

------------------------------------------
RECORD SUMMARY
------------------------------------------

Total Records        : 10,000
Valid Records        : 9,420
Rejected Records     : 580

------------------------------------------
QUALITY CHECKS
------------------------------------------

Null Issues          : 210
Duplicate Records    : 150
Invalid VIN          : 80
Invalid Dates        : 60
Out-of-Range Values  : 50
Referential Errors   : 30

------------------------------------------
QUALITY SCORE
------------------------------------------

Score                : 94.2 / 100

==========================================
```

The project requirement is that bad data is quarantined and a quality report is produced.

---

# 17. Quarantine Mechanism

Invalid records must be separated from trusted data.

```text
                    Dataset
                       |
                       v
                  Validation
                       |
              +--------+--------+
              |                 |
              v                 v
            VALID            INVALID
              |                 |
              v                 v
         Curated S3        Quarantine S3
```

A quarantined record should contain useful information such as:

```text
original_record
dataset_name
error_type
error_message
failed_rule
processed_timestamp
```

Example:

```json
{
  "vehicle_id": "BMW12345",
  "temperature": 250,
  "error_type": "OUT_OF_RANGE",
  "error_message": "Temperature is outside allowed range",
  "dataset": "telemetry"
}
```

---

# 18. AWS Glue Data Catalog

AWS Glue Data Catalog stores metadata about the curated datasets.

Example:

```text
BMW Glue Database
│
├── vehicle_master
├── telemetry
├── sales
├── maintenance
└── warranty
```

The catalog allows Athena to discover and query the curated datasets.

---

# 19. Amazon Athena

Athena is used to query validated data.

Example:

```sql
SELECT
    model,
    COUNT(*) AS vehicle_count
FROM vehicle_master
GROUP BY model;
```

Quality-report query:

```sql
SELECT
    dataset_name,
    quality_score,
    total_records,
    rejected_records
FROM data_quality_report
ORDER BY execution_timestamp DESC;
```

---

# 20. AWS Lake Formation

Lake Formation provides the governance layer for the data stored in S3.

Conceptually:

```text
                  Lake Formation
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
       RAW          CURATED       QUARANTINE
        |              |              |
        v              v              v
   Restricted      Analysts       Engineers
```

Access should be granted according to the role of the user.

---

# 21. CloudWatch Monitoring

CloudWatch provides operational visibility into the quality pipeline.

The application should log:

```text
Pipeline Started
Dataset Name
Records Received
Records Processed
Valid Records
Rejected Records
Quality Score
Validation Errors
Processing Duration
Pipeline Completed
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

# 22. Error Handling

The system should safely handle:

- Invalid input files
- Missing columns
- Incorrect data types
- Empty datasets
- S3 access failures
- PySpark processing errors
- Glue Catalog failures
- Athena failures
- Permission errors

Example:

```text
Processing
    |
    +---- Success
    |       |
    |       v
    |    Curated
    |
    +---- Failure
            |
            v
        Error Log
            |
            v
        CloudWatch
```

---

# 23. Recommended Project Structure

```text
bmw-data-quality-platform/
│
├── README.md
│
├── docs/
│   ├── architecture.png
│   ├── data_dictionary.md
│   └── data_quality_rules.md
│
├── data/
│   └── sample/
│
├── src/
│   ├── ingestion/
│   │   └── s3_loader.py
│   │
│   ├── processing/
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
│   └── utils/
│       ├── config.py
│       └── logger.py
│
├── sql/
│   └── quality_queries.sql
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
│   └── ...
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── requirements.txt
└── .gitignore
```

---

# 24. Testing

The project should contain automated tests for the major validation rules.

### Required test cases

| Test                  | Expected Result             |
| --------------------- | --------------------------- |
| Null value detection  | Failure detected            |
| Duplicate detection   | Duplicate identified        |
| VIN validation        | Invalid VIN rejected        |
| Date validation       | Invalid date rejected       |
| Range validation      | Out-of-range value rejected |
| Referential integrity | Unknown reference rejected  |
| Quality score         | Correct score generated     |
| Quarantine            | Invalid record stored       |

Example:

```text
pytest
```

Expected:

```text
8 tests passed
```

---

# 25. End-to-End Execution

The complete system should work as follows:

```text
1. Upload BMW dataset
          ↓
2. Store in S3 /raw
          ↓
3. Read using PySpark
          ↓
4. Validate schema
          ↓
5. Run quality checks
          ↓
6. Calculate quality metrics
          ↓
7. Calculate quality score
          ↓
     +----+----+
     |         |
     v         v
   Valid     Invalid
     |         |
     v         v
 Curated   Quarantine
     |
     v
Glue Catalog
     |
     v
Athena
     |
     v
Analytical Data
```

Meanwhile:

```text
Pipeline
   |
   v
CloudWatch
   |
   +── Logs
   +── Metrics
   +── Errors
```

---

# 26. MVP Scope

The **minimum working product** should contain:

```text
S3
 ↓
PySpark
 ↓
Data Quality Checks
 ↓
Valid / Invalid Separation
 ↓
Curated + Quarantine
 ↓
Quality Score
 ↓
Quality Report
 ↓
Glue Catalog
 ↓
Athena
 ↓
CloudWatch Logging
```

Do not add unnecessary advanced features until this complete flow works.

---

# 27. Acceptance Criteria

The Participant 12 project is complete when:

- [ ] BMW dataset can be loaded.
- [ ] Raw data is stored in S3.
- [ ] Null values are detected.
- [ ] Duplicate records are detected.
- [ ] Referential integrity is checked.
- [ ] Invalid VINs are detected.
- [ ] Invalid dates are detected.
- [ ] Out-of-range values are detected.
- [ ] Valid records are stored separately.
- [ ] Invalid records are quarantined.
- [ ] Data Quality Score from 0–100 is generated.
- [ ] Quality report is generated.
- [ ] Curated data is available through Glue Catalog.
- [ ] Athena can query curated data.
- [ ] CloudWatch captures processing logs.
- [ ] Automated tests pass.
- [ ] Error handling is implemented.

These acceptance requirements directly reflect the Participant 12 specification: quality checks for nulls, duplicates, referential integrity, VINs, dates and ranges; Python/PySpark with Glue Catalog, Lake Formation and CloudWatch; and quarantine plus a 0–100 quality report.

---

# 28. Final Demo Scenario

For the final demonstration:

### 1. Upload

```text
telemetry.csv
      ↓
S3/raw/telemetry/
```

### 2. Run Data Quality Engine

```text
PySpark
```

### 3. Show Results

```text
Total Records      : 10,000
Valid Records      : 9,420
Rejected Records   : 580
```

### 4. Show Quality Issues

```text
Nulls              : 210
Duplicates         : 150
Invalid VIN        : 80
Invalid Dates      : 60
Range Violations   : 50
Referential Errors : 30
```

### 5. Show Quarantine

```text
S3/quarantine/telemetry/
```

Open an invalid record and explain the failed validation rule.

### 6. Show Quality Score

```text
+--------------------------+
| DATA QUALITY SCORE       |
|                          |
|       94.2 / 100         |
|                          |
+--------------------------+
```

### 7. Show Athena

Run a query against the curated dataset.

### 8. Show CloudWatch

Demonstrate pipeline logs and processing metrics.

---

# 29. Project Outcome

The final system provides BMW data engineers with a clear mechanism to determine whether incoming data is suitable for analytical use.

```text
BMW Data
   ↓
Quality Validation
   ↓
 ┌───────────────┐
 │               │
Trusted       Untrusted
 Data           Data
 │               │
 ↓               ↓
Curated       Quarantine
 │
 ↓
Athena
 │
 ↓
Analytics

        +
        
Quality Score
        +
Quality Report
        +
CloudWatch Monitoring
        +
Lake Formation Governance
```

### Core Deliverable

> **A BMW Data Quality & Governance Platform that validates incoming datasets, quarantines bad records, generates a 0–100 Data Quality Score, and provides trusted data for downstream analytics.**
