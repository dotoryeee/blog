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