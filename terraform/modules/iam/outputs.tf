output "pipeline_role_arn" {
  description = "ARN of the pipeline IAM role."
  value       = aws_iam_role.pipeline.arn
}

output "pipeline_role_name" {
  description = "Name of the pipeline IAM role."
  value       = aws_iam_role.pipeline.name
}

output "instance_profile_arn" {
  description = "ARN of the EC2 instance profile."
  value       = aws_iam_instance_profile.pipeline.arn
}

output "instance_profile_name" {
  description = "Name of the EC2 instance profile."
  value       = aws_iam_instance_profile.pipeline.name
}
