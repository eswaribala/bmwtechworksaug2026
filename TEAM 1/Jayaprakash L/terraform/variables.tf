variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "bucket_name" {
  type = string
}

variable "glue_database_name" {
  type    = string
  default = "ev_range_analytics"
}
