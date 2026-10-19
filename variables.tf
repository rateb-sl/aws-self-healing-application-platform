variable "aws_region" {
  description = "AWS region selected for the capstone deployment."
  type        = string
  default     = "eu-central-1"

  validation {
    condition     = can(regex("^[a-z]{2}(-gov)?-[a-z]+-[0-9]+$", var.aws_region))
    error_message = "aws_region must use an AWS region format such as eu-central-1."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "capstone"

  validation {
    condition     = can(regex("^[a-z0-9-]{2,20}$", var.environment))
    error_message = "environment must contain 2-20 lowercase letters, numbers, or hyphens."
  }
}

variable "name_prefix" {
  description = "Prefix used for CloudSentinel resources."
  type        = string
  default     = "cloudsentinel"
}

variable "vpc_cidr" {
  description = "CIDR range for the CloudSentinel VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Exactly two AZ names for the capstone foundation."
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.availability_zones) == 0 || length(var.availability_zones) == 2
    error_message = "availability_zones must be empty for dynamic discovery or contain exactly two AZ names."
  }
}

variable "nat_gateway_count" {
  description = "Number of NAT gateways; one is cheaper, two improves AZ-local egress resilience."
  type        = number
  default     = 1

  validation {
    condition     = var.nat_gateway_count >= 1 && var.nat_gateway_count <= 2
    error_message = "nat_gateway_count must be 1 or 2."
  }
}
