output "bucket_name" {
  value = aws_s3_bucket.bmw_bucket.bucket
}

output "athena_database" {
  value = aws_athena_database.bmw_db.name
}

output "athena_workgroup" {
  value = aws_athena_workgroup.bmw_workgroup.name
}