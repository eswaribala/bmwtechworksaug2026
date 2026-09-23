# BMW Predictive Maintenance System

## Project Overview

The BMW Predictive Maintenance System is an end-to-end data engineering and analytics solution designed to identify vehicles that are likely to require maintenance based on historical maintenance records, telemetry data, fault history, and vehicle information.

The project processes vehicle datasets using Python and PySpark, calculates maintenance risk scores, stores curated outputs in Amazon S3, performs analytics using Amazon Athena, and visualizes insights through Amazon QuickSight.

---

## Business Objective

The primary objective of this project is to:

- Predict vehicle maintenance risks.
- Identify high-risk vehicles requiring immediate attention.
- Analyze regional maintenance trends.
- Determine primary factors contributing to maintenance risks.
- Enable proactive and data-driven maintenance planning.

---

## Technology Stack

### Programming & Processing

- Python
- PySpark

### Infrastructure

- Terraform

### AWS Services

- Amazon S3
- AWS IAM
- Amazon CloudWatch
- Amazon Athena
- Amazon QuickSight

### Documentation

- Sphinx

---

## System Architecture

```text
Vehicle CSV Files
        │
        ▼
Python Data Validation
        │
        ▼
PySpark ETL Processing
        │
        ▼
Risk Score Calculation
        │
        ▼
Curated CSV Generation
        │
        ▼
Amazon S3
        │
        ▼
Amazon Athena
        │
        ▼
Amazon QuickSight Dashboard
```

---

## Project Components

### Data Validation Layer

The validation layer verifies:

- Missing values
- Invalid records
- Data quality issues
- Schema consistency

### ETL Processing Layer

PySpark is used to:

- Read source datasets
- Transform and cleanse data
- Join datasets
- Calculate maintenance risk scores
- Categorize vehicles based on risk

### Risk Categorization

Vehicles are classified into:

- High Risk
- Medium Risk
- Low Risk

### Output Generation

Curated datasets generated:

```text
maintenance_risk_score.csv
top10_risk_vehicles.csv
```

---

## AWS Infrastructure

Infrastructure has been provisioned using Terraform.

### S3 Bucket

```text
bmw-maintenance-risk-score-blessy-2026
```

### IAM Role

```text
bmw-maintenance-role
```

### CloudWatch Log Group

```text
/aws/bmw-maintenance
```

---

## Athena Analytics

### Database

```text
bmw_predictive_maintenance
```

### Table

```text
maintenance_risk_score
```

### Records Processed

```text
210
```

### Sample Query

```sql
SELECT COUNT(*)
FROM maintenance_risk_scor*;
```

---

## QuickSight Dashboar*

### Dashboard Name

```text
BMW Predictive Maintenance Dashboard
``

### Dashboard Features

#### Total Vehicles Monitored

Displays the*total number of vehicles processed*

#### Risk Category Distribution
*Visualizes distribution across:

-*High Risk
- Medium Risk
- Low Risk*
#### Top 10 High Risk Vehicles

I*entifies vehicles requiring immedi*te maintenance attention.

#### Av*rage Risk Score by Region

Provide* regional maintenance risk insight*.

#### Primary Risk Factors Analy*is

Shows the leading causes of ma*ntenance risks:

- High Mileage
- *requent Faults
- Frequent Maintena*ce
- Temperature Trend

### Dashboard Link

```text
https://us-east-1*quicksight.aws.amazon.com/sn/accou*t/tamizh-sk/accounts/532404260630/*ashboards/65fb5bca-c7a3-45c5-a412-*10a14f38b1c
```

> Note: The dashboard is accessible only to users with access to the corresponding AWS *uickSight account and permissions.
---

## Project Results

### Key Findings

- Total vehicles analyzed* 210
- High Mileage is the most si*nificant maintenance risk factor.
* High-risk vehicles can be identif*ed proactively.
- Regional pattern in maintenance risks can be analysed.
- Business users can monitor f*eet health through interactive das*boards.

### Business Benefits

- *educed vehicle downtime
- Improved fleet monitoring
- Data-driven maintenance planning
- Better operational efficiency
- Proactive maintenance scheduling

---

## Documentati*n

Project documentation has been generated using Sphinx and includes

- Introduction
- Architecture
- *WS Infrastructure
- ETL Pipeline
-*Athena Analytics
- QuickSight Dash*oard
- Results
- Conclusion

---
## CI/CD Pipeline

GitHub Actions has been implemented to automate project validation and documentation verification.

### Pipeline Activities

- Python code validation
- Project structure validation
- Terraform validation
- Terraform formatting checks
- Sphinx documentation build

### Workflow Trigger

The CI/CD pipeline automatically executes whenever code is pushed to the repository or when a pull request is created.

### Benefits

- Ensures code quality
- Validates infrastructure configuration
- Verifies project structure
- Builds Sphinx documentation automatically
- Reduces manual verification effort

---

*# Repository Structure

```text
bm*-predictive-maintenance
│
├── terr*form/
├── data/
├── docs/
├── scre*nshots/
├── src/
├── maintenance_r*sk_score.csv
├── top10_risk_vehicl*s.csv
└── README.md
```

---

## C*nclusion

The BMW Predictive Maintanance System successfully demonstr*tes an end-to-end cloud-based analytics solution using AWS services. the system processes vehicle datasets, calculates maintenance risk scores, stores curated data in Amazon *3, performs analytics using Amazon*Athena, and delivers actionable bu*iness insights through Amazon QuickSight dashboards.

This solution ebables proactive maintenance planning and supports data-driven decision-making for vehicle fleet management.

---

## Author

**Blessy Sam**

BMW Predictive Maintenance System

2026
