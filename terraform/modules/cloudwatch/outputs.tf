output "log_group_name" {
  description = "CloudWatch log group name."
  value       = aws_cloudwatch_log_group.pipeline.name
}

output "log_group_arn" {
  description = "CloudWatch log group ARN."
  value       = aws_cloudwatch_log_group.pipeline.arn
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard."
  value       = aws_cloudwatch_dashboard.bmw.dashboard_name
}

output "dashboard_url" {
  description = "Direct URL to the CloudWatch dashboard."
  value       = "https://console.aws.amazon.com/cloudwatch/home#dashboards:name=${aws_cloudwatch_dashboard.bmw.dashboard_name}"
}

output "alarm_low_quality_arn" {
  description = "ARN of the low quality score alarm."
  value       = aws_cloudwatch_metric_alarm.low_quality_score.arn
}

output "alarm_high_error_arn" {
  description = "ARN of the high error rate alarm."
  value       = aws_cloudwatch_metric_alarm.high_error_rate.arn
}
