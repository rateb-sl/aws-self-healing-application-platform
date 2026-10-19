output "project_name" {
  description = "Stable project name used by the foundation."
  value       = local.project_name
}

output "aws_region" {
  description = "Selected AWS region."
  value       = var.aws_region
}

output "vpc_id" {
  description = "CloudSentinel VPC identifier."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet identifiers used by the ALB."
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "private_subnet_ids" {
  description = "Private subnet identifiers used by the application tier."
  value       = [for subnet in aws_subnet.private : subnet.id]
}
