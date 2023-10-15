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


