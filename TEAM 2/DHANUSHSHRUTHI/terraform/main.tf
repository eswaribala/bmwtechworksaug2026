data "aws_caller_identity" "current" {}

locals {
  bucket_name = replace(var.bucket_name, "_", "-")
  database    = "${var.project_name}_db"
}

resource "aws_s3_bucket" "data" {
  bucket        = local.bucket_name
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "datasets" {
  for_each = {
    dealer            = "dealer.csv"
    sales             = "sales.csv"
    service           = "service.csv"
    customer_feedback = "customer_feedback.csv"
  }

  bucket = aws_s3_bucket.data.id
  key    = "datasets/${each.key}/${each.value}"
  source = "${path.module}/../datasets/${each.value}"
  etag   = filemd5("${path.module}/../datasets/${each.value}")
}

resource "aws_s3_object" "athena_results_prefix" {
  bucket  = aws_s3_bucket.data.id
  key     = "athena-results/.keep"
  content = ""
}

resource "aws_iam_role" "glue" {
  name = "${var.project_name}_glue_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "glue" {
  name = "${var.project_name}-glue-access"
  role = aws_iam_role.glue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
        Resource = [aws_s3_bucket.data.arn, "${aws_s3_bucket.data.arn}/*"]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase", "glue:GetDatabases", "glue:CreateTable",
          "glue:UpdateTable", "glue:GetTable", "glue:GetTables",
          "glue:CreatePartition", "glue:BatchCreatePartition",
          "glue:GetPartition", "glue:GetPartitions", "glue:UpdatePartition"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["athena:StartQueryExecution", "athena:GetQueryExecution", "athena:GetQueryResults"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_glue_catalog_database" "scorecard" {
  name = local.database
}

resource "aws_glue_classifier" "csv" {
  name = "${var.project_name}_csv_classifier"

  csv_classifier {
    contains_header        = "PRESENT"
    delimiter              = ","
    disable_value_trimming = false
    quote_symbol           = "\""
  }
}

resource "aws_glue_catalog_table" "dealer" {
  name          = "dealer"
  database_name = aws_glue_catalog_database.scorecard.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    classification           = "csv"
    "skip.header.line.count" = "1"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.data.bucket}/datasets/dealer/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.serde2.OpenCSVSerde"
      parameters = {
        separatorChar = ","
        quoteChar     = "\""
      }
    }

    columns {
      name = "dealer_id"
      type = "string"
    }

    columns {
      name = "dealer_name"
      type = "string"
    }

    columns {
      name = "region"
      type = "string"
    }

    columns {
      name = "city"
      type = "string"
    }
  }

  depends_on = [aws_s3_object.datasets["dealer"]]
}

resource "aws_glue_crawler" "scorecard" {
  name          = "${var.project_name}_crawler"
  database_name = aws_glue_catalog_database.scorecard.name
  role          = aws_iam_role.glue.arn
  classifiers   = [aws_glue_classifier.csv.name]

  dynamic "s3_target" {
    for_each = {
      sales             = "sales"
      service           = "service"
      customer_feedback = "customer_feedback"
    }

    content {
      path = "s3://${aws_s3_bucket.data.bucket}/datasets/${s3_target.value}/"
    }
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = { AddOrUpdateBehavior = "InheritFromTable" }
      Tables     = { AddOrUpdateBehavior = "MergeNewColumns" }
    }
  })
}

resource "aws_athena_workgroup" "scorecard" {
  name = "${var.project_name}_workgroup"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.data.bucket}/athena-results/"
      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }
}
