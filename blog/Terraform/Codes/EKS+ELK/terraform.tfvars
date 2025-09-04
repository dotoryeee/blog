environment_prefix = "prod-"

region          = "ap-northeast-2"
az_1            = "ap-northeast-2a"
az_2            = "ap-northeast-2c"
vpc_cidr_block  = "10.0.0.0/16"
public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnets = ["10.0.3.0/24", "10.0.4.0/24"]
ubuntu_ami_id   = "ami-0c9c942bd7bf113a2"

logstash_instance_type = "t3.micro"
es_proxy_instance_type = "t2.micro"
grafana_instance_type = "t2.micro"
prometheus_instance_type = "t3.micro"
elasticsearch_node_type = "t3.medium.elasticsearch"
