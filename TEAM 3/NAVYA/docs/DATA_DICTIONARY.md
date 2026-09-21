\# BMW Enterprise Batch ETL — Data Dictionary



\## 1. Vehicle Master



Source file: `vehicle\_master.csv`



| Column | Data Type | Description | Validation |

|---|---|---|---|

| vehicle\_id | string | Unique identifier for a BMW vehicle | Required, unique |

| vin | string | Vehicle Identification Number | Required |

| model | string | BMW vehicle model | Required |

| model\_year | integer | Vehicle manufacturing/model year | Required, 2000–2026 |

| fuel\_type | string | Vehicle fuel/power type | Required |

| region | string | Business region | Required |

| manufacturing\_date | date | Vehicle manufacturing date | Valid date |



\### Processing



\- Null vehicle IDs are rejected.

\- Invalid model years are rejected.

\- Duplicate vehicle IDs are removed.

\- Valid records are written to processed Parquet.

\- Invalid records are written to the rejected dataset.



\---



\## 2. Sales



Source file: `sales.csv`



| Column | Data Type | Description | Validation |

|---|---|---|---|

| sale\_id | string | Unique sales transaction identifier | Required, unique |

| vehicle\_id | string | Vehicle associated with the sale | Required |

| dealer\_id | string | Dealer associated with the sale | Required |

| customer\_id | string | Customer identifier | Required |

| sale\_date | date | Date of sale | Required, valid date |

| model | string | BMW model sold | Required |

| region | string | Sales region | Null values handled |

| price | double | Unit selling price | Required, non-negative |

| quantity | integer | Number of vehicles sold | Required, greater than 0 |

| revenue | double | Calculated sales revenue | `price × quantity` |



\### Processing



\- Missing mandatory fields are rejected.

\- Negative prices are rejected.

\- Quantity values less than or equal to zero are rejected.

\- Duplicate `sale\_id` records are removed.

\- Revenue is calculated using:



`revenue = price × quantity`



\- Sales data is partitioned by `region`.

\- Null or blank regions are stored under the `Unknown` partition.

\- Valid records are written to processed Parquet.

\- Invalid records are written to the rejected dataset.



\---



\## 3. Maintenance



Source file: `maintenance.csv`



| Column | Data Type | Description | Validation |

|---|---|---|---|

| service\_id | string | Unique maintenance service identifier | Required, unique |

| vehicle\_id | string | Vehicle receiving service | Required |

| dealer\_id | string | Dealer performing service | Required |

| service\_date | date | Maintenance service date | Required, valid date |

| service\_type | string | Type of maintenance performed | Required |

| odometer | integer | Vehicle odometer reading | Required, non-negative |

| parts\_cost | double | Cost of replacement parts | Required, non-negative |

| labour\_cost | double | Labour cost | Required, non-negative |

| failure\_code | string | Failure/maintenance code | Optional |

| total\_service\_cost | double | Calculated maintenance cost | `parts\_cost + labour\_cost` |



\### Processing



\- Missing mandatory fields are rejected.

\- Negative cost values are rejected.

\- Duplicate `service\_id` records are removed.

\- Total service cost is calculated.

\- Valid records are written to processed Parquet.

\- Invalid records are written to the rejected dataset.



\---



\## 4. Dealer



Source file: `dealer.csv`



| Column | Data Type | Description | Validation |

|---|---|---|---|

| dealer\_id | string | Unique dealer identifier | Required, unique |

| dealer\_name | string | Dealer name | Required |

| city | string | Dealer city | Required |

| region | string | Business region | Required |

| capacity | integer | Dealer vehicle capacity | Required, non-negative |

| rating | double | Dealer rating | Required, 0–5 |



\### Processing



\- Missing mandatory fields are rejected.

\- Negative capacity is rejected.

\- Ratings outside the range 0–5 are rejected.

\- Duplicate `dealer\_id` records are removed.

\- Valid records are written to processed Parquet.

\- Invalid records are written to the rejected dataset.



\---



\## 5. Data Quality Summary



The ETL pipeline performs the following checks:



1\. Null value validation

2\. Duplicate record detection

3\. Numeric range validation

4\. Date validation

5\. Mandatory-field validation

6\. Deduplication

7\. Rejected-record handling



\### Latest Local Processing Results



| Dataset | Raw Records | Rejected | Valid After Validation | Final Processed |

|---|---:|---:|---:|---:|

| Vehicle Master | 1000 | 2 | 998 | 997 |

| Sales | 1000 | 3 | 997 | 996 |

| Maintenance | 1000 | 2 | 998 | 997 |

| Dealer | 100 | 2 | 98 | 97 |



\---



\## 6. Storage Format



\### Raw Layer



CSV files are stored in Amazon S3 under:



```text

raw/

├── vehicle\_master/

├── sales/

├── maintenance/

└── dealer/



Processed Layer



Validated datasets are converted to Parquet:



processed/

├── vehicle\_master/

├── sales/

├── maintenance/

└── dealer/



The Sales dataset uses Hive-style partitioning:



sales/

├── region=East/

├── region=North/

├── region=South/

├── region=Unknown/

└── region=West/

Rejected Layer



Invalid records are separated from the processed datasets:



rejected/

├── vehicle\_master/

├── sales/

├── maintenance/

└── dealer/

7\. Analytical Fields



The following derived fields are used for analytics:



Field	Calculation

revenue	price × quantity

total\_service\_cost	parts\_cost + labour\_cost



These fields support the business KPIs exposed through Athena, FastAPI, and the React dashboard.



8\. Data Consumers



The curated datasets are consumed by:



AWS Glue Data Catalog

Amazon Athena

FastAPI backend

React dashboard

SQL analytics queries

Automated validation tests



Save it with \*\*Ctrl + S\*\*, then close Notepad.



\### Step 3 — Confirm



Run:



```powershell

Get-ChildItem .\\docs | Select-Object Name

