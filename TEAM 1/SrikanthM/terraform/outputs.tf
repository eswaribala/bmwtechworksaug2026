output "aws_region" {
  description = "AWS region used by the provider."
  value       = var.aws_region
}

output "bucket_name" {
  description = "S3 bucket used by the battery health pipeline."
  value       = aws_s3_bucket.data.bucket
}

output "raw_object_keys" {
  description = "Keys uploaded to the raw S3 prefix."
  value       = [for object in aws_s3_object.raw_files : object.key]
}

output "raw_s3_path" {
  description = "S3 URI consumed by the pipeline's raw input path."
  value       = "s3://${aws_s3_bucket.data.bucket}/raw"
}

output "curated_s3_path" {
  description = "S3 URI written by the pipeline after processing."
  value       = "s3://${aws_s3_bucket.data.bucket}/curated/vehicle_health"
}

output "athena_results_s3_path" {
  description = "S3 URI to use as the Athena query result location."
  value       = "s3://${aws_s3_bucket.data.bucket}/athena-results/"
}
