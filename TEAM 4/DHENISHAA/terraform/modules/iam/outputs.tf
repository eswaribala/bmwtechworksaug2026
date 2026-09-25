output "glue_etl_role_arn" {
  description = "ARN of the Glue ETL IAM role."
  value       = aws_iam_role.glue_etl_role.arn
}

output "glue_etl_role_name" {
  description = "Name of the Glue ETL IAM role."
  value       = aws_iam_role.glue_etl_role.name
}
