resource "snowflake_warehouse" "bmw_wh" {
  name = var.warehouse_name

  warehouse_size = "XSMALL"
  warehouse_type = "STANDARD"

  auto_resume  = true
  auto_suspend = 60

  min_cluster_count = 1
  max_cluster_count = 1

  scaling_policy = "STANDARD"

  max_concurrency_level = 8

  statement_queued_timeout_in_seconds = 0
  statement_timeout_in_seconds        = 172800

  enable_query_acceleration           = true
  query_acceleration_max_scale_factor = 8
}