output "s3_bucket_name" {
  description = "BMW data S3 bucket name"
  value       = aws_s3_bucket.bmw_data.bucket
}

output "s3_bucket_arn" {
  description = "BMW data S3 bucket ARN"
  value       = aws_s3_bucket.bmw_data.arn
}

output "s3_bucket_region" {
  description = "BMW data S3 bucket region"
  value       = var.aws_region
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group"
  value       = aws_cloudwatch_log_group.bmw_pipeline.name
}

output "s3_policy_arn" {
  description = "Existing S3 policy used by Snowflake"
  value       = data.aws_iam_policy.bmw_s3_policy.arn
}