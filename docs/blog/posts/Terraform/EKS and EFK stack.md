---
draft: true
date: 2023-10-22
authors:
  - dotoryeee
categories:
  - Terraform
---
# deploy EKS and EFK
EKS 구성 및 아래 스택을 추가 구성합니다<br>
1. Prometheus + Grafana<br>
2. Logstash + OpenSearch + Cognito + Nginx Proxy
<!-- more -->

```tf title="terraform.tfvars" linenums="1"
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

```


```tf title="variables.tf" linenums="1"
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
```



```tf title="provider.tf" linenums="1"
provider "aws" {
  region = var.region
}
```


```tf title="vpc.tf" linenums="1"
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr_block
  tags = {
    Name = "l-life-${var.environment_prefix}env"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.public_subnets[0]
  map_public_ip_on_launch = true
  availability_zone       = var.az_1
  tags = {
    Name = "${var.environment_prefix}public-subnet-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.public_subnets[1]
  map_public_ip_on_launch = true
  availability_zone       = var.az_2
  tags = {
    Name = "${var.environment_prefix}public-subnet-2"
  }
}

resource "aws_subnet" "private_1" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.private_subnets[0]
  availability_zone       = var.az_1
  tags = {
    Name = "${var.environment_prefix}private-subnet-1"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.private_subnets[1]
  availability_zone       = var.az_2
  tags = {
    Name = "${var.environment_prefix}private-subnet-2"
  }
}


### NAT GW
resource "aws_eip" "nat" {
  domain   = "vpc"
}

resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_1.id
}


### Internet GW
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}
```


```tf title="route_table.tf" linenums="1"
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_2" {
  subnet_id      = aws_subnet.private_2.id
  route_table_id = aws_route_table.private.id
}

### NAT GW association

resource "aws_route" "nat_route" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.main.id
}

```


```tf title="iam.tf" linenums="1"
resource "aws_iam_role" "nginx_role" {
  name = "nginx-s3-access"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Effect = "Allow",
      Sid    = ""
    }]
  })
}

resource "aws_iam_role_policy_attachment" "nginx_s3_attachment" {
  role       = aws_iam_role.nginx_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_instance_profile" "nginx" {
  name = "nginx-s3-access"
  role = aws_iam_role.nginx_role.name
}
```


```tf title="prometheus.tf" linenums="1"
resource "aws_instance" "prometheus" {
  ami           = var.ubuntu_ami_id
  instance_type = var.prometheus_instance_type
  subnet_id     = aws_subnet.private_1.id
  tags = {
    Name = "${var.environment_prefix}prometheus"
  }
}
```


```tf title="grafana.tf" linenums="1"
### EC2
resource "aws_instance" "grafana_instance_private" {
  ami           = var.ubuntu_ami_id
  instance_type = var.grafana_instance_type
  subnet_id     = aws_subnet.private_1.id
  tags = {
    Name = "${var.environment_prefix}grafana"
  }
}

resource "aws_lb" "grafana_alb" {
  name               = "grafana-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.grafana_alb_sg.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_lb_target_group" "grafana_target_group" {
  name     = "grafana-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_listener" "grafana_ingress" {
  load_balancer_arn = aws_lb.grafana_alb.arn
  port              = "443"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.grafana_target_group.arn
  }
}

resource "aws_lb_target_group_attachment" "grafana_tg_attachment" {
  target_group_arn = aws_lb_target_group.grafana_target_group.arn
  target_id        = aws_instance.grafana_instance_private.id
}



### security Group

resource "aws_security_group" "grafana_alb_sg" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "https"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

```


```tf title="logstash.tf" linenums="1"
### EC2
resource "aws_instance" "logstash_instance_private_1_1" {
  ami           = var.ubuntu_ami_id
  instance_type = var.logstash_instance_type
  subnet_id     = aws_subnet.private_1.id
  tags = {
    Name = "${var.environment_prefix}logstash-1-1"
  }
}

resource "aws_instance" "logstash_instance_private_2_1" {
  ami           = var.ubuntu_ami_id
  instance_type = var.logstash_instance_type
  subnet_id     = aws_subnet.private_2.id
  tags = {
    Name = "${var.environment_prefix}logstash-2-1"
  }
}

resource "aws_lb" "logstash_alb" {
  name               = "logstash-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.logstash_alb_sg.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

resource "aws_lb_target_group" "logstash_target_group" {
  name     = "logstash-tg"
  port     = 5044
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_listener" "logstash_ingress" {
  load_balancer_arn = aws_lb.logstash_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.logstash_target_group.arn
  }
}

resource "aws_lb_target_group_attachment" "tg_attachment_1" {
  target_group_arn = aws_lb_target_group.logstash_target_group.arn
  target_id        = aws_instance.logstash_instance_private_1_1.id
}

resource "aws_lb_target_group_attachment" "tg_attachment_2" {
  target_group_arn = aws_lb_target_group.logstash_target_group.arn
  target_id        = aws_instance.logstash_instance_private_2_1.id
}



### security Group

resource "aws_security_group" "logstash_alb_sg" {
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 5044
    to_port     = 5044
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

```


```tf title="opensearch.tf" linenums="1"
resource "aws_security_group" "opensearch_sg" {
  vpc_id = aws_vpc.main.id
  name   = "opensearch-security-group"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticsearch_domain" "main" {
  domain_name           = "llife-was-log"
  elasticsearch_version = "7.10"

  cluster_config {
    instance_type = var.elasticsearch_node_type
    instance_count= 2
    zone_awareness_enabled = true #이 옵션을 넣지 않으면 다중 서브넷 사용이 불가능(ValidationException에러 발생)
  }

  ebs_options {
    ebs_enabled = true
    volume_size = 10
  }

  vpc_options {
    subnet_ids          = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_group_ids  = [aws_security_group.opensearch_sg.id]
  }

  cognito_options {
    enabled          = true
    user_pool_id     = aws_cognito_user_pool.main.id
    identity_pool_id = aws_cognito_identity_pool.main.id
    role_arn         = aws_iam_role.opensearch_cognito_access.arn
  }
}

resource "aws_iam_role" "opensearch_cognito_access" {
  name = "opensearch-cognito-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Principal = {
        Service = "es.amazonaws.com"
      },
      Effect = "Allow",
      Sid    = ""
    }]
  })
}

resource "aws_iam_role_policy" "opensearch_cognito_policy" {
  name = "opensearch-cognito-policy"
  role = aws_iam_role.opensearch_cognito_access.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "cognito-idp:DescribeUserPool",
        Effect   = "Allow",
        Resource = aws_cognito_user_pool.main.arn
      },
      {
        Action   = "cognito-identity:DescribeIdentityPool",
        Effect   = "Allow",
        Resource = aws_cognito_identity_pool.main.arn
      }
    ]
  })
}

```


```tf title="cognito.tf" linenums="1"
resource "aws_cognito_user_pool" "main" {
  name = "opensearch-user-pool"
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "myopensearch-domain"
  user_pool_id = aws_cognito_user_pool.main.id
}

resource "aws_cognito_identity_pool" "main" {
  identity_pool_name               = "opensearch-identity-pool"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    client_id               = aws_cognito_user_pool_client.main.id
    provider_name           = aws_cognito_user_pool.main.endpoint
    server_side_token_check = false
  }
}

resource "aws_cognito_user_pool_client" "main" {
  name            = "opensearch-client"
  user_pool_id    = aws_cognito_user_pool.main.id
  generate_secret = false
}

```


```tf title="es-proxy.tf" linenums="1"
resource "aws_instance" "es_proxy" {
  ami           = var.ubuntu_ami_id
  instance_type = var.es_proxy_instance_type
  subnet_id     = aws_subnet.public_1.id
  tags = {
    Name = "${var.environment_prefix}es-proxy"
  }

  user_data = <<-EOF
              #!/bin/bash
              sleep 10s;
              sudo apt update -y
              sudo apt install nginx -y
              aws s3 cp s3://img-resource/nginx-config.conf /etc/nginx/conf.d/
              sudo nginx -s reload
              EOF


  iam_instance_profile = aws_iam_instance_profile.nginx.name
}

```



```tf title=".tf" linenums="1"

```


```tf title=".tf" linenums="1"

```

