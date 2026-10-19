provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CloudSentinel"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
