output "bucket_name" {
  description = "Name of the S3 data lake bucket."
  value       = aws_s3_bucket.data_lake.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 data lake bucket."
  value       = aws_s3_bucket.data_lake.arn
}

output "bucket_region" {
  description = "Region of the S3 data lake bucket."
  value       = aws_s3_bucket.data_lake.region
}

output "bucket_domain_name" {
  description = "S3 bucket regional domain name."
  value       = aws_s3_bucket.data_lake.bucket_regional_domain_name
}
