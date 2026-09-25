resource "aws_glue_catalog_database" "bmw" {
  name = "${var.project}_${var.environment}"

  tags = var.tags
}

resource "aws_glue_job" "etl_job" {
  name     = "${var.project}-${var.environment}-etl-job"
  role_arn = var.role_arn

  command {
    script_location = "s3://${var.bucket_name}/scripts/glue_etl_job.py"
    python_version  = "3"
  }

  glue_version = "4.0"
  max_retries  = 0
  timeout      = 60

  default_arguments = {
    "--job-bookmark-option" = "job-bookmark-disable"
    "--enable-metrics"      = "true"
    "--bucket"              = var.bucket_name
  }

  tags = var.tags
}

resource "aws_glue_crawler" "curated" {
  name          = "${var.project}-${var.environment}-curated-crawler"
  role          = var.role_arn
  database_name = aws_glue_catalog_database.bmw.name
  s3_target {
    path = "s3://${var.bucket_name}/curated/"
  }

  tags = var.tags
}
