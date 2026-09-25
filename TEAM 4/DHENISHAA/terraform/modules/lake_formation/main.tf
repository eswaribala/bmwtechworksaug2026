resource "aws_lakeformation_data_lake_settings" "this" {
  admins = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
}

data "aws_caller_identity" "current" {}
