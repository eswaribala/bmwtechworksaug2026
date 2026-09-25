output "bucket_name" {
  description = "The bucket name for the data lake."
  value       = aws_s3_bucket.data_lake.id
}

output "bucket_arn" {
  description = "The ARN of the data lake bucket."
  value       = aws_s3_bucket.data_lake.arn
}
