output "s3_bucket_name" {
  description = "BMW warranty S3 bucket name"
  value       = aws_s3_bucket.bmw_warranty.bucket
}

output "s3_bucket_arn" {
  description = "BMW warranty S3 bucket ARN"
  value       = aws_s3_bucket.bmw_warranty.arn
}