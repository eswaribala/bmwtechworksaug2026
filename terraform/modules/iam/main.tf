/**
 * IAM Module — Pipeline Role & Policies
 * Creates the IAM role used by the BMW data quality pipeline.
 *
 * Policies granted:
 *   - S3: read raw, write curated/quarantine/reports/logs
 *   - CloudWatch Logs & Metrics
 *   - Glue: catalog read/write (register curated tables)
 *   - Athena: run queries against curated data
 */

# ────────────────────────────────────────────────
# Trust Policy (EC2 + ECS can assume this role)
# ────────────────────────────────────────────────

data "aws_iam_policy_document" "trust" {
  statement {
    sid    = "AllowEC2AndECSAssume"
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = [
        "ec2.amazonaws.com",
        "ecs-tasks.amazonaws.com",
      ]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "pipeline" {
  name               = var.role_name
  assume_role_policy = data.aws_iam_policy_document.trust.json
  description        = "BMW Data Quality pipeline execution role (Participant 12 / Pod D)"

  tags = {
    Name    = var.role_name
    Purpose = "DataPipeline"
  }
}

# ────────────────────────────────────────────────
# S3 Policy — Read raw, write curated/quarantine/reports/logs
# ────────────────────────────────────────────────

data "aws_iam_policy_document" "s3" {
  statement {
    sid    = "ListBucket"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetBucketLocation",
      "s3:ListBucketMultipartUploads",
    ]
    resources = [var.bucket_arn]
  }

  statement {
    sid    = "ReadRaw"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:HeadObject",
    ]
    resources = ["${var.bucket_arn}/raw/*"]
  }

  statement {
    sid    = "WriteAll"
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:AbortMultipartUpload",
      "s3:ListMultipartUploadParts",
      "s3:GetObject",
      "s3:GetObjectVersion",
    ]
    resources = [
      "${var.bucket_arn}/raw/*",
      "${var.bucket_arn}/curated/*",
      "${var.bucket_arn}/quarantine/*",
      "${var.bucket_arn}/reports/*",
      "${var.bucket_arn}/logs/*",
    ]
  }
}

resource "aws_iam_policy" "s3" {
  name        = "${var.project_name}-s3-policy"
  description = "BMW pipeline S3 read/write permissions"
  policy      = data.aws_iam_policy_document.s3.json
}

resource "aws_iam_role_policy_attachment" "s3" {
  role       = aws_iam_role.pipeline.name
  policy_arn = aws_iam_policy.s3.arn
}

# ────────────────────────────────────────────────
# CloudWatch Policy — Logs + Metrics
# ────────────────────────────────────────────────

data "aws_iam_policy_document" "cloudwatch" {
  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams",
      "logs:DescribeLogGroups",
    ]
    resources = [
      "arn:aws:logs:${var.region}:${var.account_id}:log-group:${var.cloudwatch_log_group}",
      "arn:aws:logs:${var.region}:${var.account_id}:log-group:${var.cloudwatch_log_group}:*",
    ]
  }

  statement {
    sid    = "CloudWatchMetrics"
    effect = "Allow"
    actions = [
      "cloudwatch:PutMetricData",
      "cloudwatch:GetMetricStatistics",
      "cloudwatch:ListMetrics",
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "cloudwatch:namespace"
      values   = ["BMW/DataQuality"]
    }
  }
}

resource "aws_iam_policy" "cloudwatch" {
  name        = "${var.project_name}-cloudwatch-policy"
  description = "BMW pipeline CloudWatch Logs and Metrics permissions"
  policy      = data.aws_iam_policy_document.cloudwatch.json
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.pipeline.name
  policy_arn = aws_iam_policy.cloudwatch.arn
}

# ────────────────────────────────────────────────
# Glue Policy — Register and read Glue Data Catalog
# ────────────────────────────────────────────────

data "aws_iam_policy_document" "glue" {
  statement {
    sid    = "GlueCatalog"
    effect = "Allow"
    actions = [
      "glue:CreateDatabase",
      "glue:GetDatabase",
      "glue:GetDatabases",
      "glue:CreateTable",
      "glue:UpdateTable",
      "glue:GetTable",
      "glue:GetTables",
      "glue:DeleteTable",
      "glue:BatchCreatePartition",
      "glue:CreatePartition",
      "glue:UpdatePartition",
      "glue:GetPartition",
      "glue:GetPartitions",
      "glue:BatchDeletePartition",
    ]
    resources = [
      "arn:aws:glue:${var.region}:${var.account_id}:catalog",
      "arn:aws:glue:${var.region}:${var.account_id}:database/bmw_data_quality",
      "arn:aws:glue:${var.region}:${var.account_id}:table/bmw_data_quality/*",
    ]
  }
}

resource "aws_iam_policy" "glue" {
  name        = "${var.project_name}-glue-policy"
  description = "BMW pipeline Glue Data Catalog read/write"
  policy      = data.aws_iam_policy_document.glue.json
}

resource "aws_iam_role_policy_attachment" "glue" {
  role       = aws_iam_role.pipeline.name
  policy_arn = aws_iam_policy.glue.arn
}

# ────────────────────────────────────────────────
# Athena Policy — Run queries on curated data
# ────────────────────────────────────────────────

data "aws_iam_policy_document" "athena" {
  statement {
    sid    = "AthenaQuery"
    effect = "Allow"
    actions = [
      "athena:StartQueryExecution",
      "athena:GetQueryExecution",
      "athena:GetQueryResults",
      "athena:StopQueryExecution",
      "athena:ListQueryExecutions",
      "athena:GetWorkGroup",
      "athena:ListWorkGroups",
    ]
    resources = [
      "arn:aws:athena:${var.region}:${var.account_id}:workgroup/bmw-data-quality",
    ]
  }

  statement {
    sid    = "AthenaResultsS3"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]
    resources = [
      "${var.bucket_arn}/reports/athena-results/*",
      var.bucket_arn,
    ]
  }
}

resource "aws_iam_policy" "athena" {
  name        = "${var.project_name}-athena-policy"
  description = "BMW pipeline Athena query permissions"
  policy      = data.aws_iam_policy_document.athena.json
}

resource "aws_iam_role_policy_attachment" "athena" {
  role       = aws_iam_role.pipeline.name
  policy_arn = aws_iam_policy.athena.arn
}

# ────────────────────────────────────────────────
# Instance Profile (for EC2 use-cases)
# ────────────────────────────────────────────────

resource "aws_iam_instance_profile" "pipeline" {
  name = "${var.project_name}-instance-profile"
  role = aws_iam_role.pipeline.name
}
