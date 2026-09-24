# ============================================================
# BMW SNOWFLAKE CAPSTONE - IAM CONFIGURATION
# ============================================================

# ------------------------------------------------------------
# EXISTING S3 POLICY
# ------------------------------------------------------------
# The S3 policy already exists in AWS.
# Terraform will reference it, not recreate or delete it.

data "aws_iam_policy" "bmw_s3_policy" {
  arn = "arn:aws:iam::532404260630:policy/snowflake-data-warehousing-dev-s3-policy"
}


# ------------------------------------------------------------
# IAM ROLE FOR SNOWFLAKE
# ------------------------------------------------------------

resource "aws_iam_role" "snowflake_capstone_role" {
  name = "vrr-snowflake-capstone"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          AWS = "arn:aws:iam::192929863221:user/vqc72000-s"
        }

        Action = "sts:AssumeRole"

        Condition = {
          StringEquals = {
            "sts:ExternalId" = "PN92455_SFCRole=4_Zrih67xNpZl2K9hu9Vzxi8drlAo="
          }
        }
      }
    ]
  })

  tags = {
    Project     = "BMW-Snowflake-Capstone"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}


# ------------------------------------------------------------
# ATTACH EXISTING S3 POLICY TO NEW SNOWFLAKE ROLE
# ------------------------------------------------------------

resource "aws_iam_role_policy_attachment" "snowflake_capstone_s3_access" {
  role       = aws_iam_role.snowflake_capstone_role.name
  policy_arn = data.aws_iam_policy.bmw_s3_policy.arn
}


# ------------------------------------------------------------
# OUTPUTS
# ------------------------------------------------------------

output "snowflake_iam_role_name" {
  description = "IAM role used by Snowflake"
  value       = aws_iam_role.snowflake_capstone_role.name
}

output "snowflake_iam_role_arn" {
  description = "IAM role ARN used by Snowflake"
  value       = aws_iam_role.snowflake_capstone_role.arn
}