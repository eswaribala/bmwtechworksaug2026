module "s3" {
  source = "./modules/s3"

  bucket_name = local.bucket_name
  environment = var.environment
  project     = var.project_name
  tags        = local.common_tags
}

module "iam" {
  source = "./modules/iam"

  project     = var.project_name
  environment = var.environment
  tags        = local.common_tags
}

module "glue" {
  source = "./modules/glue"

  project     = var.project_name
  environment = var.environment
  bucket_name = module.s3.bucket_name
  bucket_arn  = module.s3.bucket_arn
  role_arn    = module.iam.glue_etl_role_arn
  tags        = local.common_tags
}

module "athena" {
  source = "./modules/athena"

  project     = var.project_name
  environment = var.environment
  bucket_name = module.s3.bucket_name
  bucket_arn  = module.s3.bucket_arn
  tags        = local.common_tags
}

module "monitoring" {
  source = "./modules/monitoring"

  project     = var.project_name
  environment = var.environment
  tags        = local.common_tags
}

module "lake_formation" {
  source = "./modules/lake_formation"

  bucket_arn   = module.s3.bucket_arn
  database_arn = module.glue.database_arn
  project      = var.project_name
  environment  = var.environment
  tags         = local.common_tags
}

module "quicksight" {
  count  = var.quicksight_enabled ? 1 : 0
  source = "./modules/quicksight"

  project            = var.project_name
  environment        = var.environment
  notification_email = "example@example.com"
  tags               = local.common_tags
}
