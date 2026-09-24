variable "snowflake_account" {
  description = "Snowflake account identifier"
  type        = string
}

variable "snowflake_user" {
  description = "Snowflake username"
  type        = string
}

variable "snowflake_password" {
  description = "Snowflake password"
  type        = string
  sensitive   = true
}

variable "snowflake_role" {
  description = "Snowflake role used by Terraform"
  type        = string
  default     = "ACCOUNTADMIN"
}

variable "snowflake_authenticator" {
  description = "Snowflake authentication method"
  type        = string
  default     = "snowflake"
}

variable "database_name" {
  description = "BMW analytics database"
  type        = string
  default     = "BMW_ANALYTICS"
}

variable "warehouse_name" {
  description = "BMW analytics warehouse"
  type        = string
  default     = "BMW_WH"
}

variable "schema_name" {
  description = "BMW analytics schema"
  type        = string
  default     = "BMW_DATA"
}

variable "analyst_role_name" {
  description = "Read-only BMW analyst role"
  type        = string
  default     = "BMW_ANALYST_READONLY"
}

variable "analyst_user_name" {
  description = "Snowflake user receiving the analyst role"
  type        = string
  default     = "ARUL"
}