output "database_name" {
  description = "Name of the Glue Catalog database."
  value       = aws_glue_catalog_database.bmw.name
}

output "database_arn" {
  description = "ARN of the Glue Catalog database."
  value       = aws_glue_catalog_database.bmw.arn
}

output "job_name" {
  description = "Name of the Glue ETL job."
  value       = aws_glue_job.etl_job.name
}
