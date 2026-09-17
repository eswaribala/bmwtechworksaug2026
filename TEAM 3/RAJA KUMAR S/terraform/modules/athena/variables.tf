variable "project_name" {
  description = "Project name prefix."
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 data lake bucket (used for Athena query results)."
  type        = string
}

variable "glue_database" {
  description = "Name of the Glue database to query."
  type        = string
}
