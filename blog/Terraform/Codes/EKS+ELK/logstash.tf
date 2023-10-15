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
