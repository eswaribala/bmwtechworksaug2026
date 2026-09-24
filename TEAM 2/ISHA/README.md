# BMW Service Centre Capacity Intelligence

## Project Overview

This project is an end-to-end data engineering, analytics, and business intelligence solution designed to identify overloaded and underutilized BMW service centres.

The solution ingests maintenance and dealer data, cleans and transforms it using PySpark, stores processed datasets in Amazon S3, calculates business KPIs using Amazon Athena, and presents actionable insights through Amazon QuickSight dashboards.

---

## Business Problem

BMW operates multiple service centres across different regions. Uneven service workloads can lead to:

- overloaded service centres
- increased customer wait times
- inefficient resource allocation
- underutilized service facilities
- higher operational costs

The objective is to monitor service centre efficiency and provide actionable operational insights.

---

## Project Objectives

The solution enables BMW operations teams to:

- monitor service centre utilization
- identify overloaded dealerships
- identify underutilized dealerships
- analyze repair cost patterns
- compare dealer performance across regions
- improve operational planning and resource allocation

---

## Architecture

```text
Maintenance CSV              Dealer CSV
       |                         |
       +-----------+-------------+
                   |
                   v
            PySpark ETL
                   |
                   v
      maintenance_cleaned.csv
      maintenance_dealer_joined.csv
                   |
                   v
          Amazon S3 (Terraform)
                   |
                   v
             Amazon Athena
                   |
                   v
      dealer_capacity_metrics
                (view)
                   |
                   v
        Amazon QuickSight
                   |
                   v
          Business Insights
```

---

## Technology Stack

### Data Engineering

- Python
- PySpark

### Cloud Services

- Amazon S3
- Amazon Athena
- Amazon QuickSight

### Infrastructure as Code

- Terraform

### Analytics

- SQL
- Athena views

---

## Source Datasets

### Dealer Dataset

This dataset contains dealer information.

#### Fields

```text
dealer_id
dealer_name
city
region
capacity
rating
```

---

### Maintenance Dataset

This dataset contains service records.

#### Fields

```text
service_id
vehicle_id
dealer_id
service_date
service_type
odometer
parts_cost
labour_cost
failure_code
```

---

## ETL Pipeline

### Step 1: Data Ingestion

Source files:

```text
dealer_large.csv
maintenance_large_100k.csv
```

---

### Step 2: Data Cleaning

#### Null Handling

Records containing missing values are removed.

#### Duplicate Removal

Duplicate maintenance records are removed.

#### Data Validation

The pipeline validates:

- dealer IDs
- service IDs
- cost values

---

### Step 3: Data Transformation

#### Repair Cost Calculation

A new column is created as follows:

```text
repair_cost = parts_cost + labour_cost
```

---

### Step 4: Data Integration

Maintenance data is joined with dealer data using:

```text
dealer_id
```

Output:

```text
maintenance_dealer_joined.csv
```

---

## Infrastructure Provisioning

Infrastructure is provisioned using Terraform.

### Resources Created

#### Amazon S3

Stores processed datasets and query output.

Bucket structure:

```text
s3://<bucket-name>/
├── processed/
│   ├── maintenance_cleaned.csv
│   └── maintenance_dealer_joined.csv
└── athena-results/
```

---

#### Athena Database

```text
bmw_service_db
```

---

#### Athena Workgroup

```text
bmw-capstone-workgroup
```

---

## Athena Analytics Layer

### Source Table

```text
maintenance_dealer_joined
```

### KPI View

```text
dealer_capacity_metrics
```

This Athena view provides the metrics required for dashboard reporting and operational analysis.

---

# Key Performance Indicators (KPIs)

## KPI 1: Services Per Day

Measures the average number of services completed by a dealer per day.

Formula:

```sql
COUNT(*) /
COUNT(DISTINCT service_date)
```

Business Value:

- Dealer workload analysis
- Service centre performance monitoring

---

## KPI 2: Average Repair Cost

Measures average repair expenditure.

Formula:

```sql
AVG(repair_cost)
```

Business Value:

- Cost analysis
- Financial monitoring

---

## KPI 3: Average Service Interval

Measures the average number of days between consecutive vehicle service visits.

Functions Used:

```sql
LAG()
DATE_DIFF()
```

Business Value:

- Customer servicing behaviour
- Maintenance planning

---

## KPI 4: Dealer Capacity Utilization

Measures service centre utilization.

Formula:

```sql
(total_services / capacity) * 100
```

Business Value:

- Resource planning
- Service centre efficiency

---

# Dealer Classification Logic

Dealers are classified based on utilization thresholds.

```sql
CASE
    WHEN capacity_utilization_pct > 90
        THEN 'OVERLOADED'

    WHEN capacity_utilization_pct < 60
        THEN 'UNDER_UTILIZED'

    ELSE 'OPTIMAL'
END
```

## Categories

### OVERLOADED

```text
Utilization > 90%
```

### UNDER_UTILIZED

```text
Utilization < 60%
```

### OPTIMAL

```text
Utilization between 60% and 90%
```

---

# Acceptance Criteria

✅ Flag dealers exceeding configurable capacity thresholds.

Implementation:

```text
OVERLOADED      → Utilization > 90*
UNDER_UTILIZED  → Utilization < 6*%
OPTIMAL         → Utilization be*ween 60% and 90%
```

All dealers *re automatically classified using *usiness rules within the Athena KP* View.

---

# Amazon QuickSight D*shboard

## Dashboard Screenshot

*ocs/dashboard.png

---

## Executi*e KPI Cards

The dashboard provide*:

- Total Dealers
- Average Servi*es Per Day
- Average Repair Cost
-*Average Capacity Utilization %

--*

## Dashboard Visualizations

###*Dealer Capacity Utilization Rankin*

Shows utilization percentage by *ealer.

---

### Dealer Status Dis*ribution

Shows distribution of:

* Overloaded Dealers
- Under-utilized Dealers
- Optimal Dealers

---

*## Average Capacity Utilization by*Region

Compares utilization across:

```text
North
South
East
West
`*`

---

### Average Repair Cost by*Region

Compares regional repair e*penditure.

---

### Dealer KPI Su*mary Table

Provides detailed deal*r-level metrics:

- Dealer Name
- *ity
- Region
- Services Per Day
- *verage Repair Cost
- Average Servi*e Interval
- Capacity Utilization *
- Dealer Status

---

# Dashboard*Filters

Interactive dashboard con*rols:

- Region
- City
- Dealer St*tus
- Dealer Name

---

# Business*Insights

The solution enables use*s to:

- Identify overloaded servi*e centres.
- Identify under-utiliz*d service centres.
- Analyze regio*al utilization trends.
- Compare r*pair cost patterns.
- Monitor deal*rship performance.
- Improve opera*ional decision-making.

---

# Rep*sitory Structure

```text
project-*oot/
│
├── README.md
│
├── docs/
│*  ├── architecture.png
│   ├── ath*na-view.png
│   └── dashboard.png
*
├── src/
│   └── cmodule/
│      *├── data/
│       │   ├── dealer_l*rge.csv
│       │   └── maintenanc*_large_100k.csv
│       │
│       *── etl.py
│       ├── analytics.py*│       └── __init__.py
│
├── terr*form/
│   ├── provider.tf
│   ├── *ariables.tf
│   ├── s3.tf
│   ├── *thena.tf
│   └── outputs.tf
│
├── *aintenance_cleaned.csv
├── mainten*nce_dealer_joined.csv
│
└── tests/*```

---

# How to Run the Project*
## Step 1: Execute ETL

```bash
p*thon src/cmodule/etl.py
```

Gener*tes:

```text
maintenance_cleaned.*sv
maintenance_dealer_joined.csv
`*`

---

## Step 2: Deploy Infrastr*cture

```bash
cd terraform

terra*orm init
terraform validate
terraf*rm plan
terraform apply
```

---

*# Step 3: Upload Data to S3

Terra*orm uploads processed datasets to *mazon S3.

---

## Step 4: Create *thena Table

Create:

```text
main*enance_dealer_joined
```

table ov*r S3 data.

---

## Step 5: Create*KPI View

Create:

```text
dealer_*apacity_metrics
```

Athena view.
*---

## Step 6: Build QuickSight D*shboard

Connect QuickSight to:

`*`text
Athena
→ bmw_service_db
→ de*ler_capacity_metrics
``*

Create*KPI cards, charts, filters, and de*ler insights.

---

* Future Enhancements*
- Real-time Kafka integration
- P*edictive maintenance analytics
- M*-based service demand forecasting
* Automated alerting
- CloudWatch m*nitoring
- Advanced regional repor*ing

---

# Conclusion

This proje*t successfully demonstrates an end*to-end BMW Service Centre Capacity*Intelligence platform using PySpar*, Terraform, Amazon S3, Athena, an* QuickSight.

The solution provide* operational visibility through KP*-driven analytics and enables BMW operations teams to identify overloaded and under-utilized service centres for improved planning, efficiency, and decision-making.