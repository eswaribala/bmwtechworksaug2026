output "bucket_name" {
  description = "Name of the S3 data lake bucket."
  value       = module.s3.bucket_name
}

output "bucket_arn" {
  description = "ARN of the S3 data lake bucket."
  value       = module.s3.bucket_arn
}

output "glue_database_name" {
  description = "Glue database name."
  value       = module.glue.database_name
}

output "glue_job_name" {
  description = "Glue ETL job name."
  value       = module.glue.job_name
}

output "athena_workgroup" {
  description = "Athena workgroup name."
  value       = module.athena.workgroup_name
}

output "log_group_name" {
  description = "CloudWatch log group used for monitoring."
  value       = module.monitoring.log_group_name
}
