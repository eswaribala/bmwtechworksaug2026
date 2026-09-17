/**
 * CloudWatch Module — Logs, Metric Filters & Dashboard
 * Monitors the BMW Data Quality pipeline.
 *
 * Metric Filters extract:
 *   - QualityScore   from log events
 *   - ErrorCount     from log events
 *   - PipelineRuns   from log events
 *   - RejectedRecords from log events
 *
 * Alarms notify (no SNS — just CloudWatch visibility):
 *   - Quality score drops below threshold
 *   - Error count exceeds 5 in 5 minutes
 */

# ────────────────────────────────────────────────
# Log Group
# ────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "pipeline" {
  name              = var.log_group_name
  retention_in_days = var.retention_days

  tags = {
    Name    = var.log_group_name
    Purpose = "DataQualityPipeline"
  }
}

# ────────────────────────────────────────────────
# Metric Filters
# ────────────────────────────────────────────────

# Filter 1 — Quality Score
resource "aws_cloudwatch_log_metric_filter" "quality_score" {
  name           = "${var.project_name}-quality-score"
  log_group_name = aws_cloudwatch_log_group.pipeline.name
  pattern        = "[timestamp, level, logger, ..., label=\"QUALITY_SCORE\", score]"

  metric_transformation {
    name          = "QualityScore"
    namespace     = "BMW/DataQuality"
    value         = "$score"
    default_value = "0"
    unit          = "None"
  }
}

# Filter 2 — Error Count
resource "aws_cloudwatch_log_metric_filter" "error_count" {
  name           = "${var.project_name}-error-count"
  log_group_name = aws_cloudwatch_log_group.pipeline.name
  pattern        = "[timestamp, level=\"ERROR\", ...]"

  metric_transformation {
    name          = "ErrorCount"
    namespace     = "BMW/DataQuality"
    value         = "1"
    default_value = "0"
    unit          = "Count"
  }
}

# Filter 3 — Pipeline Runs
resource "aws_cloudwatch_log_metric_filter" "pipeline_runs" {
  name           = "${var.project_name}-pipeline-runs"
  log_group_name = aws_cloudwatch_log_group.pipeline.name
  pattern        = "[timestamp, level, logger, ..., label=\"PIPELINE_END\"]"

  metric_transformation {
    name          = "PipelineRuns"
    namespace     = "BMW/DataQuality"
    value         = "1"
    default_value = "0"
    unit          = "Count"
  }
}

# Filter 4 — Rejected Records
resource "aws_cloudwatch_log_metric_filter" "rejected_records" {
  name           = "${var.project_name}-rejected-records"
  log_group_name = aws_cloudwatch_log_group.pipeline.name
  pattern        = "[timestamp, level, logger, ..., label=\"REJECTED_RECORDS\", count]"

  metric_transformation {
    name          = "RejectedRecords"
    namespace     = "BMW/DataQuality"
    value         = "$count"
    default_value = "0"
    unit          = "Count"
  }
}

# ────────────────────────────────────────────────
# Alarms (CloudWatch visibility only, no SNS)
# ────────────────────────────────────────────────

# Alarm 1 — Low Quality Score
resource "aws_cloudwatch_metric_alarm" "low_quality_score" {
  alarm_name          = "${var.project_name}-low-quality-score"
  alarm_description   = "BMW data quality score dropped below ${var.alarm_low_quality_threshold}%"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "QualityScore"
  namespace           = "BMW/DataQuality"
  period              = 300
  statistic           = "Average"
  threshold           = var.alarm_low_quality_threshold
  treat_missing_data  = "notBreaching"

  # No SNS actions — alarm is visible on CloudWatch dashboard only
  alarm_actions = []
  ok_actions    = []

  tags = {
    Name = "${var.project_name}-low-quality-score"
  }
}

# Alarm 2 — High Error Rate
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.project_name}-high-error-rate"
  alarm_description   = "BMW pipeline error count exceeded 5 in 5 minutes"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ErrorCount"
  namespace           = "BMW/DataQuality"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  treat_missing_data  = "notBreaching"

  alarm_actions = []

  tags = {
    Name = "${var.project_name}-high-error-rate"
  }
}

# ────────────────────────────────────────────────
# Dashboard
# ────────────────────────────────────────────────

resource "aws_cloudwatch_dashboard" "bmw" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 2
        properties = {
          markdown = "# 🚗 BMW Data Quality & Governance Platform\n**Participant 12 | Pod D** — Real-time pipeline monitoring dashboard"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 2
        width  = 8
        height = 6
        properties = {
          title  = "Quality Score (Latest)"
          view   = "singleValue"
          region = var.region
          metrics = [
            ["BMW/DataQuality", "QualityScore", { stat = "Average", period = 300 }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 2
        width  = 8
        height = 6
        properties = {
          title  = "Rejected Records (Last Hour)"
          view   = "singleValue"
          region = var.region
          metrics = [
            ["BMW/DataQuality", "RejectedRecords", { stat = "Sum", period = 3600 }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 2
        width  = 8
        height = 6
        properties = {
          title  = "Pipeline Runs (Today)"
          view   = "singleValue"
          region = var.region
          metrics = [
            ["BMW/DataQuality", "PipelineRuns", { stat = "Sum", period = 86400 }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 8
        width  = 24
        height = 6
        properties = {
          title  = "Quality Score — Trend (Last 7 Days)"
          view   = "timeSeries"
          region = var.region
          metrics = [
            ["BMW/DataQuality", "QualityScore", { stat = "Average", period = 3600, color = "#2ca02c", label = "Quality Score" }]
          ]
          yAxis = { left = { min = 0, max = 100 } }
          annotations = {
            horizontal = [
              { value = var.alarm_low_quality_threshold, label = "Alert Threshold", color = "#d62728" }
            ]
          }
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 14
        width  = 12
        height = 6
        properties = {
          title  = "Errors vs Rejected Records"
          view   = "timeSeries"
          region = var.region
          metrics = [
            ["BMW/DataQuality", "ErrorCount", { stat = "Sum", period = 3600, color = "#d62728", label = "Errors" }],
            ["BMW/DataQuality", "RejectedRecords", { stat = "Sum", period = 3600, color = "#ff7f0e", label = "Rejected" }]
          ]
        }
      },
      {
        type   = "alarm"
        x      = 12
        y      = 14
        width  = 12
        height = 6
        properties = {
          title  = "Active Alarms"
          alarms = [
            aws_cloudwatch_metric_alarm.low_quality_score.arn,
            aws_cloudwatch_metric_alarm.high_error_rate.arn,
          ]
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 20
        width  = 24
        height = 6
        properties = {
          title  = "Recent Pipeline Logs"
          region = var.region
          query  = "SOURCE '${var.log_group_name}' | fields @timestamp, @message | sort @timestamp desc | limit 50"
          view   = "table"
        }
      }
    ]
  })
}
