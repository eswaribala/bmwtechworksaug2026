# BMW Dealer Scoreboard Performance

## Documentation

Read the Sphinx documentation for project setup, AWS architecture, operations,
data scoring, and troubleshooting:

[Open the BMW Dealer Scoreboard Performance documentation](https://dhanushshruthi27.github.io/bmw_dealer_score_performance/)

This project provisions an AWS analytics foundation for calculating dealer performance scores from sales, service, and customer feedback data.

## Prerequisites

- AWS account with permissions to create S3, Glue, Athena, IAM, and related resources.
- AWS CLI configured with credentials for the target account.
- Terraform >= 1.5.0.
- Access to Amazon Athena. QuickSight is optional and is not provisioned by Terraform.

## Project configuration

The default values are stored in `terraform/terraform.tfvars`:

- AWS region: `<region>`
- Project name: `bmw_dealer_score_performace`
- Environment: `<environment>`
- S3 bucket request name: `<bucket_name>`

S3 bucket names are globally unique. If the bucket name is already taken, change `bucket_name` in `terraform/terraform.tfvars` to another globally unique lowercase name.

## Deploy the infrastructure

From the repository root:

```powershell
Set-Location .\terraform
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan
```

Review the plan before applying it. Terraform creates the S3 bucket, uploads the CSV files, creates the Glue database and tables, configures the crawler, and creates the Athena workgroup.

After deployment, display the generated resource names with:

```powershell
terraform output
```

## Run the Glue crawler

The crawler discovers the `sales`, `service`, and `customer_feedback` tables. The `dealer` table is defined directly in Terraform.

Start the crawler from the AWS Console, or with the AWS CLI:

```powershell
aws glue start-crawler `
  --name <crawler_name> `
  --region <region>
```

Wait until the crawler state is `READY` before running the Athena view SQL. You can check the state with:

```powershell
aws glue get-crawler `
  --name <crawler_name> `
  --region <region> `
  --query 'Crawler.State' `
  --output text
```

## Create the scoring view in Athena

1. Open Amazon Athena in `<region>`.
2. Select workgroup `<workgroup_name>`.
3. Open `sql/dealer_score_view.sql`.
4. Run the complete statement.
5. Confirm that the view `bmw_dealer_score_performace_db.dealer_score_vw` was created.

The query reads data for the 2025 calendar year and calculates a normalized score using:

- Revenue: 50%
- Service count: 30%
- Average customer rating: 20%

Example query:

```sql
SELECT *
FROM bmw_dealer_score_performace_db.dealer_score_vw
ORDER BY dealer_rank;
```

## Optional QuickSight setup

QuickSight is not configured by the Terraform code. To build a dashboard manually:

1. Create an Athena data source in the same AWS region.
2. Select workgroup `<workgroup_name>`.
3. Select database `bmw_dealer_score_performace_db` and view `dealer_score_vw`.
4. Import the view into SPICE or query it directly.
5. Build visuals for score, rank, revenue, service count, rating, and region.

## Cleanup

To remove the Terraform-managed resources:

```powershell
Set-Location .\terraform
terraform destroy
```

The S3 bucket uses `force_destroy = false`, so remove its objects manually before destroying it if Terraform reports that the bucket is not empty. Review the destroy plan carefully because it deletes cloud infrastructure and stored data.

## Repository layout

```text
datasets/                 Source CSV files
sql/dealer_score_view.sql Athena view and scoring logic
terraform/                AWS infrastructure as code
README.md                 Setup and execution guide
README_ARCHITECTURE.md   Project details and architecture
docs/                    Sphinx documentation
```


