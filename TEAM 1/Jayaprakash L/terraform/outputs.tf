output "bucket_name" {
  value = aws_s3_bucket.ev_analytics.bucket
}

output "glue_database" {
  value = aws_glue_catalog_database.ev.name
}
