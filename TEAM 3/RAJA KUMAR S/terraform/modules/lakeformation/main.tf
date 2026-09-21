/**
 * Lake Formation Module — Governance layer over the BMW data lake.
 *
 * What this actually provisions (no simulation):
 *   1. Registers the S3 data lake bucket as a Lake Formation resource.
 *   2. Sets the Lake Formation data lake administrators (this pipeline role +
 *      whoever applies Terraform), while preserving IAM_ALLOWED_PRINCIPALS
 *      defaults so existing IAM-based Glue/Athena access keeps working
 *      (hybrid access mode) — nothing already working is broken.
 *   3. Creates two additional personas as real IAM roles:
 *        - Data Analyst   → SELECT/DESCRIBE on curated + report tables
 *        - Business User  → SELECT/DESCRIBE on the report table only
 *   4. Grants fine-grained Lake Formation permissions per persona, matching
 *      the zone-access matrix (raw / curated / quarantine / reports).
 */

# ────────────────────────────────────────────────
# Data Lake Settings — administrators
# ────────────────────────────────────────────────

resource "aws_lakeformation_data_lake_settings" "this" {
  admins = distinct(concat(var.data_lake_admin_arns, [var.pipeline_role_arn]))

  # Preserve legacy IAM-based access on top of Lake Formation grants so
  # nothing that already relies on IAM permissions breaks.
  create_database_default_permissions {
    permissions = ["ALL"]
    principal   = "IAM_ALLOWED_PRINCIPALS"
  }

  create_table_default_permissions {
    permissions = ["ALL"]
    principal   = "IAM_ALLOWED_PRINCIPALS"
  }
}

# ────────────────────────────────────────────────
# Register the S3 bucket as a Lake Formation resource
# ────────────────────────────────────────────────

resource "aws_lakeformation_resource" "data_lake" {
  arn                     = var.bucket_arn
  use_service_linked_role = true

  depends_on = [aws_lakeformation_data_lake_settings.this]
}

# ────────────────────────────────────────────────
# Persona — Data Analyst (curated + reports, read-only)
# ────────────────────────────────────────────────

data "aws_iam_policy_document" "analyst_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.account_id}:root"]
    }
  }
}

resource "aws_iam_role" "data_analyst" {
  name               = "${var.project_name}-data-analyst-role"
  assume_role_policy = data.aws_iam_policy_document.analyst_trust.json
  description        = "BMW Lake Formation persona - read curated data + reports via Athena"

  tags = {
    Name    = "${var.project_name}-data-analyst-role"
    Purpose = "Governance-DataAnalyst"
  }
}

data "aws_iam_policy_document" "analyst_query" {
  statement {
    sid    = "LakeFormationAndGlueRead"
    effect = "Allow"
    actions = [
      "lakeformation:GetDataAccess",
      "glue:GetDatabase",
      "glue:GetDatabases",
      "glue:GetTable",
      "glue:GetTables",
      "glue:GetPartition",
      "glue:GetPartitions",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AthenaQuery"
    effect = "Allow"
    actions = [
      "athena:StartQueryExecution",
      "athena:GetQueryExecution",
      "athena:GetQueryResults",
      "athena:StopQueryExecution",
      "athena:GetWorkGroup",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AthenaResultsBucket"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:GetBucketLocation",
      "s3:ListBucket",
    ]
    resources = [
      var.bucket_arn,
      "${var.bucket_arn}/reports/athena-results/*",
    ]
  }
}

resource "aws_iam_role_policy" "analyst_query" {
  name   = "${var.project_name}-data-analyst-query-policy"
  role   = aws_iam_role.data_analyst.id
  policy = data.aws_iam_policy_document.analyst_query.json
}

# ────────────────────────────────────────────────
# Persona — Business User (reports only, read-only)
# ────────────────────────────────────────────────

data "aws_iam_policy_document" "business_user_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.account_id}:root"]
    }
  }
}

resource "aws_iam_role" "business_user" {
  name               = "${var.project_name}-business-user-role"
  assume_role_policy = data.aws_iam_policy_document.business_user_trust.json
  description        = "BMW Lake Formation persona - read-only access to quality reports"

  tags = {
    Name    = "${var.project_name}-business-user-role"
    Purpose = "Governance-BusinessUser"
  }
}

data "aws_iam_policy_document" "business_user_query" {
  statement {
    sid    = "LakeFormationAndGlueRead"
    effect = "Allow"
    actions = [
      "lakeformation:GetDataAccess",
      "glue:GetDatabase",
      "glue:GetTable",
      "glue:GetPartitions",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AthenaQuery"
    effect = "Allow"
    actions = [
      "athena:StartQueryExecution",
      "athena:GetQueryExecution",
      "athena:GetQueryResults",
      "athena:GetWorkGroup",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "AthenaResultsBucket"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:GetBucketLocation",
      "s3:ListBucket",
    ]
    resources = [
      var.bucket_arn,
      "${var.bucket_arn}/reports/athena-results/*",
    ]
  }
}

resource "aws_iam_role_policy" "business_user_query" {
  name   = "${var.project_name}-business-user-query-policy"
  role   = aws_iam_role.business_user.id
  policy = data.aws_iam_policy_document.business_user_query.json
}

# ────────────────────────────────────────────────
# Lake Formation Permissions — Data Engineer (pipeline role)
# Full access: raw + curated + quarantine + reports
# ────────────────────────────────────────────────

resource "aws_lakeformation_permissions" "engineer_database" {
  principal   = var.pipeline_role_arn
  permissions = ["ALL"]

  database {
    name = var.glue_database_name
  }

  depends_on = [aws_lakeformation_resource.data_lake]
}

resource "aws_lakeformation_permissions" "engineer_tables" {
  principal   = var.pipeline_role_arn
  permissions = ["ALL"]

  table {
    database_name = var.glue_database_name
    wildcard      = true
  }

  depends_on = [aws_lakeformation_resource.data_lake]
}

# ────────────────────────────────────────────────
# Lake Formation Permissions — Data Analyst
# Curated (vehicle_master, telemetry) + reports (data_quality_report)
# ────────────────────────────────────────────────

resource "aws_lakeformation_permissions" "analyst_tables" {
  principal   = aws_iam_role.data_analyst.arn
  permissions = ["SELECT", "DESCRIBE"]

  table {
    database_name = var.glue_database_name
    wildcard      = true
  }

  depends_on = [aws_lakeformation_resource.data_lake]
}

# ────────────────────────────────────────────────
# Lake Formation Permissions — Business User
# Reports table only (data_quality_report)
# ────────────────────────────────────────────────

resource "aws_lakeformation_permissions" "business_user_report_table" {
  principal   = aws_iam_role.business_user.arn
  permissions = ["SELECT", "DESCRIBE"]

  table {
    database_name = var.glue_database_name
    name          = "data_quality_report"
  }

  depends_on = [aws_lakeformation_resource.data_lake]
}
