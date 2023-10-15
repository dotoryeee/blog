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