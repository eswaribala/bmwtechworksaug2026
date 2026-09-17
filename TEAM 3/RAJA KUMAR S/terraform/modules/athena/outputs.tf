output "workgroup_name" {
  description = "Name of the Athena workgroup."
  value       = aws_athena_workgroup.bmw.name
}

output "workgroup_arn" {
  description = "ARN of the Athena workgroup."
  value       = aws_athena_workgroup.bmw.arn
}

output "output_location" {
  description = "S3 path where Athena query results are stored."
  value       = "s3://${var.bucket_name}/reports/athena-results/"
}
