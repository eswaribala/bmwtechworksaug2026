variable "snowflake_organization" {
  type        = string
  description = "Snowflake organization name"
}

variable "snowflake_account" {
  type        = string
  description = "Snowflake account name"
}

variable "snowflake_user" {
  type        = string
  description = "Snowflake administrative username"
}

variable "snowflake_password" {
  type        = string
  description = "Snowflake administrative password"
  sensitive   = true
}

variable "database_name" {
  type        = string
  description = "BMW sales database name"
  default     = "BMW_SALES_DB"
}

variable "schema_name" {
  type        = string
  description = "BMW sales schema name"
  default     = "SALES"
}

variable "warehouse_name" {
  type        = string
  description = "BMW analytics warehouse name"
  default     = "BMW_ANALYTICS_WH"
}

variable "role_name" {
  type        = string
  description = "BMW analytics role name"
  default     = "BMW_ANALYTICS_ROLE"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "eu-north-1"
}

variable "aws_account_id" {
  type        = string
  description = "AWS account ID"
}

variable "s3_bucket_name" {
  type        = string
  description = "S3 bucket containing BMW sales data"
  default     = "anshul-ki-balti"
}

variable "s3_bmw_prefix" {
  type        = string
  description = "S3 prefix containing the BMW Parquet file"
  default     = "processed/bmw/"
}

variable "snowflake_iam_user_arn" {
  type        = string
  description = "Snowflake IAM user ARN used in AWS trust policy"
  default     = "arn:aws:iam::008349342067:user/ifjz1000-s"
}

# We generate/use our own external ID so both Terraform and AWS
# can use the same value.
variable "snowflake_external_id" {
  type        = string
  description = "External ID used for Snowflake to assume the AWS IAM role"
  sensitive   = true
}