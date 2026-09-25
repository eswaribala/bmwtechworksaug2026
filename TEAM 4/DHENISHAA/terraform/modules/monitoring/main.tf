resource "aws_cloudwatch_log_group" "bmw" {
  name              = "/aws/glue/${var.project}/${var.environment}"
  retention_in_days = 14

  tags = var.tags
}
