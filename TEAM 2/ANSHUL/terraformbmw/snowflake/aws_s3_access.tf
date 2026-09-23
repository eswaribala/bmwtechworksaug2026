# ---------------------------------------------------------
# IAM Role assumed by Snowflake
# ---------------------------------------------------------

resource "aws_iam_role" "snowflake_s3_role" {
  name = "BMWSnowflakeS3Role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          AWS = var.snowflake_iam_user_arn
        }

        Action = "sts:AssumeRole"

        Condition = {
          StringEquals = {
            "sts:ExternalId" = var.snowflake_external_id
          }
        }
      }
    ]
  })

  tags = {
    Project = "BMW-Sales-Analytics"
    Purpose = "Snowflake-S3-Access"
  }
}


# ---------------------------------------------------------
# S3 permissions for Snowflake
# ---------------------------------------------------------

resource "aws_iam_role_policy" "snowflake_s3_read" {

  name = "BMW-Snowflake-S3-Read"

  role = aws_iam_role.snowflake_s3_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [

      # Allow Snowflake to list the bucket
      {
        Effect = "Allow"

        Action = [
          "s3:ListBucket",
        ]

        Resource = "arn:aws:s3:::${var.s3_bucket_name}"

        Condition = {
          StringLike = {
            "s3:prefix" = [
              "${var.s3_bmw_prefix}*"
            ]
          }
        }
      },

      # Allow Snowflake to read BMW Parquet files
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject"
        ]

        Resource = "arn:aws:s3:::${var.s3_bucket_name}/${var.s3_bmw_prefix}*"
      }
    ]
  })
}