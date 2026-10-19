locals {
  project_name = "${var.name_prefix}-${var.environment}"

  selected_azs = length(var.availability_zones) == 2 ? var.availability_zones : slice(
    data.aws_availability_zones.available.names,
    0,
    2,
  )

  public_subnets = {
    az_a = {
      az   = local.selected_azs[0]
      cidr = cidrsubnet(var.vpc_cidr, 8, 0)
    }
    az_b = {
      az   = local.selected_azs[1]
      cidr = cidrsubnet(var.vpc_cidr, 8, 2)
    }
  }

  private_subnets = {
    az_a = {
      az   = local.selected_azs[0]
      cidr = cidrsubnet(var.vpc_cidr, 8, 1)
    }
    az_b = {
      az   = local.selected_azs[1]
      cidr = cidrsubnet(var.vpc_cidr, 8, 3)
    }
  }

  nat_keys = var.nat_gateway_count == 2 ? ["az_a", "az_b"] : ["az_a"]
}
