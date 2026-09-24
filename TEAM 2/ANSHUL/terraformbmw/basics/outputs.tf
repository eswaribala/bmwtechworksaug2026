output "account_id" { value = data.aws_caller_identity.current.account_id }
output "region" { value = data.aws_region.current.region }
output "bucket_name" { value = aws_s3_bucket.demo.id }
