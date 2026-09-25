variable "project" {
  description = "Project name used for QuickSight resources."
  type        = string
}

variable "environment" {
  description = "Environment name used for QuickSight resources."
  type        = string
}

variable "notification_email" {
  description = "Email used for QuickSight account notifications."
  type        = string
  default     = "example@example.com"
}

variable "tags" {
  description = "Tags applied to QuickSight resources."
  type        = map(string)
}
