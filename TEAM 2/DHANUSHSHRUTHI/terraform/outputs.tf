output "s3_bucket_name" {
  value = aws_s3_bucket.data.bucket
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.data.arn
}

output "glue_database_name" {
  value = aws_glue_catalog_database.scorecard.name
}

output "glue_crawler_name" {
  value = aws_glue_crawler.scorecard.name
}

output "athena_results_location" {
  value = "s3://${aws_s3_bucket.data.bucket}/athena-results/"
}

output "athena_workgroup_name" {
  value = aws_athena_workgroup.scorecard.name
}
