output "log_group_name" {
  description = "CloudWatch log group name for Glue monitoring."
  value       = aws_cloudwatch_log_group.bmw.name
}
