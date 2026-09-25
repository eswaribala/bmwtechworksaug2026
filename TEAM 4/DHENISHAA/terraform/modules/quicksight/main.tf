resource "aws_quicksight_account_subscription" "this" {
  account_name          = "bmw-serverless-data-lake"
  notification_email    = var.notification_email
  authentication_method = "IAM_AND_QUICKSIGHT"
  edition               = "STANDARD"
}
