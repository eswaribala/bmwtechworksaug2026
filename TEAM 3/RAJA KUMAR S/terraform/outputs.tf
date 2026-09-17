output "s3_bucket_name" {
  description = "Name of the BMW data lake S3 bucket."
  value       = module.s3.bucket_name
}

output "s3_bucket_arn" {
  description = "ARN of the BMW data lake S3 bucket."
  value       = module.s3.bucket_arn
}

output "s3_bucket_region" {
  description = "AWS region of the S3 bucket."
  value       = module.s3.bucket_region
}

output "pipeline_role_arn" {
  description = "ARN of the IAM role used by the data quality pipeline."
  value       = module.iam.pipeline_role_arn
}

output "pipeline_role_name" {
  description = "Name of the IAM role used by the data quality pipeline."
  value       = module.iam.pipeline_role_name
}

output "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group."
  value       = module.cloudwatch.log_group_name
}

output "cloudwatch_dashboard_url" {
  description = "URL to the CloudWatch dashboard for BMW Data Quality."
  value       = module.cloudwatch.dashboard_url
}

output "glue_database_name" {
  description = "Name of the Glue Data Catalog database."
  value       = module.glue.database_name
}

output "athena_workgroup_name" {
  description = "Name of the Athena workgroup for querying curated data."
  value       = module.athena.workgroup_name
}

output "athena_output_location" {
  description = "S3 path where Athena query results are stored."
  value       = module.athena.output_location
}

output "s3_folder_structure" {
  description = "Logical folder layout inside the bucket."
  value = {
    raw_telemetry      = "s3://${module.s3.bucket_name}/raw/telemetry/"
    raw_vehicle_master = "s3://${module.s3.bucket_name}/raw/vehicle_master/"
    curated            = "s3://${module.s3.bucket_name}/curated/"
    quarantine         = "s3://${module.s3.bucket_name}/quarantine/"
    reports            = "s3://${module.s3.bucket_name}/reports/"
    logs               = "s3://${module.s3.bucket_name}/logs/"
  }
}

