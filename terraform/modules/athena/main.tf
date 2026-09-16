/**
 * Athena Module — Workgroup for querying curated BMW data
 *
 * Spec §19: "Athena is used to query validated data."
 *
 * Creates:
 *   - Athena workgroup: bmw-data-quality
 *   - Query results stored in s3://<bucket>/reports/athena-results/
 */

resource "aws_athena_workgroup" "bmw" {
  name        = "${var.project_name}"
  description = "BMW Data Quality Platform — Athena workgroup for querying curated data (Participant 12)"
  state       = "ENABLED"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${var.bucket_name}/reports/athena-results/"

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }

    engine_version {
      selected_engine_version = "Athena engine version 3"
    }
  }

  tags = {
    Name    = "${var.project_name}-workgroup"
    Purpose = "CuratedDataQuery"
  }
}

# ────────────────────────────────────────────────
# Named Query Examples (pre-built queries from spec §19)
# ────────────────────────────────────────────────

resource "aws_athena_named_query" "vehicle_count_by_model" {
  name        = "bmw-vehicle-count-by-model"
  description = "Count vehicles by model from the curated vehicle_master table"
  workgroup   = aws_athena_workgroup.bmw.name
  database    = var.glue_database

  query = <<-SQL
    SELECT
        model,
        COUNT(*) AS vehicle_count
    FROM vehicle_master
    GROUP BY model
    ORDER BY vehicle_count DESC;
  SQL
}

resource "aws_athena_named_query" "quality_report_summary" {
  name        = "bmw-quality-report-summary"
  description = "Latest data quality scores across all pipeline runs"
  workgroup   = aws_athena_workgroup.bmw.name
  database    = var.glue_database

  query = <<-SQL
    SELECT
        dataset_name,
        quality_score,
        total_records,
        valid_records,
        rejected_records,
        execution_timestamp
    FROM data_quality_report
    ORDER BY execution_timestamp DESC
    LIMIT 20;
  SQL
}

resource "aws_athena_named_query" "telemetry_battery_stats" {
  name        = "bmw-telemetry-battery-stats"
  description = "Battery level statistics from curated telemetry data"
  workgroup   = aws_athena_workgroup.bmw.name
  database    = var.glue_database

  query = <<-SQL
    SELECT
        vehicle_id,
        COUNT(*) AS event_count,
        ROUND(AVG(battery_level), 2) AS avg_battery,
        MIN(battery_level) AS min_battery,
        MAX(battery_level) AS max_battery
    FROM telemetry
    GROUP BY vehicle_id
    ORDER BY avg_battery ASC;
  SQL
}
