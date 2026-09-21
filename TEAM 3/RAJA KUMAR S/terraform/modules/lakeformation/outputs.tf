output "data_analyst_role_arn" {
  description = "ARN of the Data Analyst persona role (SELECT/DESCRIBE on curated + reports)."
  value       = aws_iam_role.data_analyst.arn
}

output "data_analyst_role_name" {
  description = "Name of the Data Analyst persona role."
  value       = aws_iam_role.data_analyst.name
}

output "business_user_role_arn" {
  description = "ARN of the Business User persona role (SELECT/DESCRIBE on reports only)."
  value       = aws_iam_role.business_user.arn
}

output "business_user_role_name" {
  description = "Name of the Business User persona role."
  value       = aws_iam_role.business_user.name
}

output "lakeformation_resource_arn" {
  description = "ARN of the S3 bucket registered as a Lake Formation resource."
  value       = aws_lakeformation_resource.data_lake.arn
}
