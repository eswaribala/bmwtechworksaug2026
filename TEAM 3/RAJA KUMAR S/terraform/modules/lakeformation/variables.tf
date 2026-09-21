variable "project_name" {
  description = "Prefix used for all resource names."
  type        = string
}

variable "account_id" {
  description = "AWS account ID."
  type        = string
}

variable "region" {
  description = "AWS region."
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 data lake bucket."
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 data lake bucket."
  type        = string
}

variable "athena_output_location" {
  description = "S3 URI where Athena stores query results (for analyst/business-user query access)."
  type        = string
}

variable "glue_database_name" {
  description = "Name of the Glue Data Catalog database governed by Lake Formation."
  type        = string
}

variable "pipeline_role_arn" {
  description = "ARN of the existing pipeline (Data Engineer) IAM role."
  type        = string
}

variable "pipeline_role_name" {
  description = "Name of the existing pipeline (Data Engineer) IAM role."
  type        = string
}

variable "data_lake_admin_arns" {
  description = "Additional IAM user/role ARNs to register as Lake Formation data lake administrators (e.g. the operator applying Terraform)."
  type        = list(string)
  default     = []
}
