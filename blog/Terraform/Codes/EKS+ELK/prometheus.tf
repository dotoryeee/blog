resource "aws_instance" "prometheus" {
  ami           = var.ubuntu_ami_id
  instance_type = var.prometheus_instance_type
  subnet_id     = aws_subnet.private_1.id
  tags = {
    Name = "${var.environment_prefix}prometheus"
  }
}