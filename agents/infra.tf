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

# -------------------------
# Data Layer
# -------------------------
resource "aws_db_instance" "db" {
  identifier = "app-db"
  # Add DynamoDB encryption at rest and in transit features
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name = aws_db_subnet_group.db.name
}

resource "aws_dynamodb_table" "dynamo" {
  name = "session-table"
  # Add DynamoDB encryption at rest and in transit features
  attribute_definitions = [
    {
      attribute_name = "id"
      attribute_type = "S"
    }
  ]
  key_schema = [
    {
      attribute_name = "id"
      key_type = "HASH"
    }
  ]
  table_status = "ACTIVE"
}

resource "aws_elasticache_cluster" "cache" {
  cluster_id = "redis-cache"
  # Add Elasticache encryption at rest and in transit features
  vpc_security_group_ids = [aws_security_group.cache.id]
  engine = "redis"
  engine_version = "6.x"
}

# -------------------------
# Storage
# -------------------------
resource "aws_s3_bucket" "assets" {
  bucket = "app-assets-bucket"
  # Add S3 bucket encryption at rest and in transit features
  bucket_acl = "private"
}

resource "aws_efs_file_system" "efs" {
  # Add EFS encryption at rest and in transit features
  create_file_system = true
}

# -------------------------
# Integration
# -------------------------
resource "aws_sqs_queue" "queue" {
  name = "job-queue"
  # Add SQS encryption at rest and in transit features
  visibility_timeout_seconds = 300
}

resource "aws_sns_topic" "alerts" {
  name = "alerts-topic"
  # Add SNS encryption at rest and in transit features
  subscription = aws_sns_topic_subscription.alerts
}

# -------------------------
# Security
# -------------------------
resource "aws_iam_role" "app_role" {
  name = "app-role"
  # Add IAM role policies for Lambda, EC2, and S3
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_kms_key" "kms" {
  # Add KMS key for encryption
  description = "KMS key for encryption"
  key_usage = "ENCRYPT_DECRYPT"
  key_status = "Enabled"
}

resource "aws_secretsmanager_secret" "secret" {
  name = "db-secret"
  # Add Secrets Manager secret for database credentials
  description = "Database credentials"
}