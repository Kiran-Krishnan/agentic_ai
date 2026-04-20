# -------------------------
# Compute Layer
# -------------------------
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

# -------------------------
# Integration
# -------------------------
resource "aws_sqs_queue" "queue" {
  name = "job-queue"
}

resource "aws_sns_topic" "alerts" {
  name = "alerts-topic"
}

# -------------------------
# Security
# -------------------------
resource "aws_iam_role" "app_role" {
  name = "app-role"
}

resource "aws_kms_key" "kms" {}

resource "aws_secretsmanager_secret" "secret" {
  name = "db-secret"
}
# -------------------------
# Data Layer
# -------------------------
resource "aws_db_instance" "db" {
  identifier = "app-db"
}

resource "aws_dynamodb_table" "dynamo" {
  name = "session-table"
}

resource "aws_elasticache_cluster" "cache" {
  cluster_id = "redis-cache"
}

# -------------------------
# Storage
# -------------------------
resource "aws_s3_bucket" "assets" {
  bucket = "app-assets-bucket"
}

resource "aws_efs_file_system" "efs" {}