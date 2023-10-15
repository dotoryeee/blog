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
