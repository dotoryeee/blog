module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "17.0.0"

  cluster_name = "garden-eks"
  cluster_version = 1.26
  subnets      = module.vpc.private_subnets

  tags = {
    Terraform = "true"
    Project   = "EKS"
  }

  vpc_id = module.vpc.vpc_id

  node_groups_defaults = {
    ami_type  = "AL2_x86_64"
    disk_size = 30
    instance_type = "t3.micro" 
  }

  node_groups = {
    master = {
      desired_capacity = 1
      max_capacity     = 3
      min_capacity     = 1
    }
    data = {
      desired_capacity = 3
      max_capacity     = 3
      min_capacity     = 3
    }
  }
}