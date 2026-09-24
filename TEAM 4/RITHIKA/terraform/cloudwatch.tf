resource "aws_cloudwatch_log_group" "bmw_pipeline" {
  name              = "/bmw/${var.project_name}/${var.environment}"
  retention_in_days = 14

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Purpose     = "BMW data pipeline logging"
  }
}