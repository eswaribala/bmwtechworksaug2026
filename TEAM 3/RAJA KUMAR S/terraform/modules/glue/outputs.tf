output "database_name" {
  description = "Name of the Glue Data Catalog database."
  value       = aws_glue_catalog_database.bmw.name
}

output "database_arn" {
  description = "ARN of the Glue Data Catalog database."
  value       = "arn:aws:glue:${var.region}:${var.account_id}:database/bmw_data_quality"
}

output "table_vehicle_master" {
  description = "Name of the vehicle_master Glue table."
  value       = aws_glue_catalog_table.vehicle_master.name
}

output "table_telemetry" {
  description = "Name of the telemetry Glue table."
  value       = aws_glue_catalog_table.telemetry.name
}

output "table_data_quality_report" {
  description = "Name of the data_quality_report Glue table."
  value       = aws_glue_catalog_table.data_quality_report.name
}
