# Compute Layer
resource "aws_instance" "app" {
  subnet_id = aws_subnet.private.id
  tags = { Name = "app-server" }
}

resource "aws_autoscaling_group" "asg" {
  desired_capacity = 2
}

resource "aws_lambda_function" "worker" {
  function_name = "background-worker"
}

resource "aws_ecs_cluster" "ecs" {
  name = "ecs-cluster"
}

resource "aws_efs_file_system" "efs" {}

# Integration
resource "aws_sqs_queue" "queue" {
  name = "job-queue"
}

resource "aws_sns_topic" "alerts" {
  name = "alerts-topic"
}

# Security
resource "aws_iam_role" "app_role" {
  name = "app-role"
}

resource "aws_kms_key" "kms" {}

resource "aws_secretsmanager_secret" "secret" {
  name = "db-secret"
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id
}

resource "aws_eip" "nat" {}

resource "aws_security_group" "web_sg" {
  vpc_id = aws_vpc.main.id
}

# Edge Layer
resource "aws_lb" "alb" {
  subnets = [aws_subnet.public.id]
}

resource "aws_cloudfront_distribution" "cdn" {
  enabled = true
}

resource "aws_wafv2_web_acl" "waf" {
  name  = "web-acl"
  scope = "REGIONAL"
}