/**
 * BMW Data Quality & Governance Platform — Root Terraform Module
 * Participant 12 | Pod D
 *
 * Architecture (per spec):
 *   S3 (raw / curated / quarantine / reports / logs)
 *   → IAM Role (S3 + CloudWatch + Glue + Athena)
 *   → CloudWatch (logs, metric filters, dashboard)
 *   → Glue Data Catalog (database + tables over curated/)
 *   → Athena Workgroup (query curated data)
 */

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id  = data.aws_caller_identity.current.account_id
  region      = data.aws_region.current.name
  bucket_name = var.s3_bucket_name != "" ? var.s3_bucket_name : "${var.project_name}-${local.account_id}"
  role_name   = var.pipeline_role_name != "" ? var.pipeline_role_name : "bmw-data-quality-pipeline-role"
}

# ╔══════════════════════════════════════════════════════╗
# ║  S3  —  Data Lake Bucket                            ║
# ╚══════════════════════════════════════════════════════╝
module "s3" {
  source = "./modules/s3"

  bucket_name               = local.bucket_name
  force_destroy             = var.s3_force_destroy
  versioning_enabled        = var.s3_versioning_enabled
  lifecycle_quarantine_days = var.s3_lifecycle_quarantine_days
  lifecycle_logs_days       = var.s3_lifecycle_logs_days
  project_name              = var.project_name
}

# ╔══════════════════════════════════════════════════════╗
# ║  IAM  —  Pipeline Role                              ║
# ║  S3 read/write + CloudWatch + Glue + Athena         ║
# ╚══════════════════════════════════════════════════════╝
module "iam" {
  source = "./modules/iam"

  role_name            = local.role_name
  bucket_arn           = module.s3.bucket_arn
  bucket_name          = local.bucket_name
  cloudwatch_log_group = var.cloudwatch_log_group
  project_name         = var.project_name
  account_id           = local.account_id
  region               = local.region
}

# ╔══════════════════════════════════════════════════════╗
# ║  CloudWatch  —  Logs / Metrics / Dashboard          ║
# ╚══════════════════════════════════════════════════════╝
module "cloudwatch" {
  source = "./modules/cloudwatch"

  log_group_name              = var.cloudwatch_log_group
  retention_days              = var.cloudwatch_retention_days
  alarm_low_quality_threshold = var.alarm_low_quality_threshold
  project_name                = var.project_name
  bucket_name                 = local.bucket_name
  region                      = local.region
}

# ╔══════════════════════════════════════════════════════╗
# ║  Glue  —  Data Catalog (database + tables)          ║
# ╚══════════════════════════════════════════════════════╝
module "glue" {
  source = "./modules/glue"

  project_name = var.project_name
  bucket_name  = local.bucket_name
  region       = local.region
  account_id   = local.account_id

  depends_on = [module.s3]
}

# ╔══════════════════════════════════════════════════════╗
# ║  Athena  —  Workgroup for querying curated data     ║
# ╚══════════════════════════════════════════════════════╝
module "athena" {
  source = "./modules/athena"

  project_name     = var.project_name
  bucket_name      = local.bucket_name
  glue_database    = module.glue.database_name

  depends_on = [module.s3, module.glue]
}

# ╔══════════════════════════════════════════════════════╗
# ║  Lake Formation  —  Fine-grained data governance    ║
# ║  Registers the bucket, sets admins, creates the     ║
# ║  Data Analyst / Business User personas, and grants  ║
# ║  per-table SELECT/DESCRIBE permissions.             ║
# ╚══════════════════════════════════════════════════════╝
module "lakeformation" {
  source = "./modules/lakeformation"

  project_name            = var.project_name
  account_id              = local.account_id
  region                  = local.region
  bucket_name             = local.bucket_name
  bucket_arn              = module.s3.bucket_arn
  athena_output_location  = module.athena.output_location
  glue_database_name      = module.glue.database_name
  pipeline_role_arn       = module.iam.pipeline_role_arn
  pipeline_role_name      = module.iam.pipeline_role_name
  data_lake_admin_arns    = var.lakeformation_admin_arns

  depends_on = [module.s3, module.glue, module.iam, module.athena]
}
