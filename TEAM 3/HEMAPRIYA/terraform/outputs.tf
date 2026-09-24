output "s3_bucket_name" {
  description = "Name of the BMW inventory S3 bucket"
  value       = aws_s3_bucket.inventory.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the BMW inventory S3 bucket"
  value       = aws_s3_bucket.inventory.arn
}

output "aws_region" {
  description = "AWS region where the infrastructure is deployed"
  value       = var.aws_region
}