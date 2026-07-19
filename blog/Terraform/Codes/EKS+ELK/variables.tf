variable "environment_prefix" {
}

variable "region" {
  default     = "ap-northeast-2"
}

variable "az_1" {
  default     = "ap-northeast-2a"
}

variable "az_2" {
  default     = "ap-northeast-2c"
}

variable "vpc_cidr_block" {
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  type        = list(string)
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "ubuntu_ami_id" {
  description = "Ubuntu 22 AMI ID"
  default     = "ami-0c9c942bd7bf113a2"
}

variable "logstash_instance_type" {
    default   = "t3.micro"
}

variable "es_proxy_instance_type" {
    default   = "t2.micro"
}

variable "grafana_instance_type" {
    default   = "t2.micro"
}

variable "prometheus_instance_type" {
    default   = "t3.micro"
}

variable "elasticsearch_node_type" {
    default   = "t3.medium.elasticsearch"
}