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
