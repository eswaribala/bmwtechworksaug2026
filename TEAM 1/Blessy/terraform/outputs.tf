output "bucket_name" {
  value = aws_s3_bucket.bmw_bucket.bucket
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.bmw_logs.name
}

output "iam_role" {
  value = aws_iam_role.bmw_role.name
}