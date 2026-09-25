<<<<<<< HEAD
# Dhenishaa-Datalake-Project
=======
# BMW Serverless Data Lake Analytics

This project implements a serverless AWS data lake for BMW vehicle analytics using Terraform, Python, PySpark, S3, AWS Glue, Athena, Lake Formation, and QuickSight.

## Business problem
BMW generates large quantities of vehicle telemetry, sales, maintenance, and warranty data. The goal is to store this data in a scalable, serverless, cost-aware data lake and make it easy for analysts to query and visualize insights without managing traditional database infrastructure.

## Architecture summary

The project uses the following architecture:

- Synthetic BMW datasets generated locally
- Raw data stored in Amazon S3
- Python validation and preprocessing
- PySpark ETL for cleaning, type conversion, and Parquet conversion
- Partitioned curated data in S3
- AWS Glue crawler and Data Catalog
- Amazon Athena for SQL queries
- Lake Formation for governance
- CloudWatch for logs and alarms
- QuickSight dashboard design for analytics
- Terraform for infrastructure deployment
- GitHub Actions for CI/CD validation

## Repository structure

- src/bmw_data_lake: Python package for config, validation, processing, and utilities
- jobs: Glue ETL scripts
- scripts: operational scripts for generation and AWS interactions
- sql: Athena queries
- tests: pytest suite
- terraform: Terraform root and modules
- docs: architecture and operational documentation
- .github/workflows: CI/CD pipelines

## Prerequisites

- Python 3.11+
- Terraform 1.5+
- AWS CLI configured with a valid profile or role
- Git
- Optional: AWS account with permissions to deploy the required services

## Python setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## AWS CLI setup

```bash
aws configure --profile default
aws sts get-caller-identity --profile default
```

## Terraform setup

```bash
cd terraform
terraform init
terraform validate
terraform plan
```

## Running tests

```bash
pytest
```

## Project phases

This project is implemented in phases and follows a Terraform-first approach. The project is intentionally organized so you can learn each component before moving to the next layer.

## Important notes

- Do not hardcode AWS credentials.
- Do not run terraform apply without explicit approval.
- QuickSight and Lake Formation may require account-level prerequisites.
- Actual Athena scan measurements must be captured from AWS and not invented.

## License

This project is intended for learning and demonstration use and is distributed under the MIT license.
>>>>>>> ac045f6 (Add CI CD workflows)
