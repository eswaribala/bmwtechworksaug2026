# Athena Database

resource "aws_athena_database" "bmw_db" {
  name          = "bmw_service_db"
  bucket        = aws_s3_bucket.bmw_bucket.bucket
  force_destroy = true
}

# Athena Workgroup

resource "aws_athena_workgroup" "bmw_workgroup" {
  name = "bmw-capstone-workgroup"

  configuration {
    enforce_workgroup_configuration = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.bmw_bucket.bucket}/athena-results/"
    }
  }
}