# Component 1: User Interface (Web or Mobile App)
resource "aws_api_gateway" "ui" {
  name        = "ai-bank-chatbot-ui"
  description = "User Interface for AI Bank Chatbot"
}

resource "aws_api_gateway_resource" "ui_resource" {
  rest_api_id = aws_api_gateway.ui.id
  parent_id   = aws_api_gateway.ui.root_resource_id
  path_part   = "ui"
}

resource "aws_api_gateway_method" "ui_get" {
  rest_api_id = aws_api_gateway.ui.id
  resource_id = aws_api_gateway_resource.ui_resource.id
  http_method = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "ui_get_integration" {
  rest_api_id = aws_api_gateway.ui.id
  resource_id = aws_api_gateway_resource.ui_resource.id
  http_method = aws_api_gateway_method.ui_get.http_method
  integration_http_method = "POST"
  type        = "AWS"
  uri         = "arn:aws:apigateway:${aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.chatbot_function.arn}/invocations"
}

# Component 2: AI Chatbot (Lambda Function or API Gateway)
resource "aws_lambda_function" "chatbot_function" {
  filename      = "lambda_function_payload.zip"
  function_name = "ai-bank-chatbot-lambda"
  handler       = "index.handler"
  runtime       = "nodejs14.x"
}

# Component 3: Database (DynamoDB or RDS)
resource "aws_dynamodb_table" "database" {
  name           = "ai-bank-chatbot-database"
  billing_mode   = "PROVISIONED"
  read_capacity_units = 5
  write_capacity_units = 5
  attribute {
    name = "id"
    type = "S"
  }
}

# Component 4: Security (IAM and Cognito)
resource "aws_iam_role" "chatbot_role" {
  name        = "ai-bank-chatbot-role"
  description = "Role for AI Bank Chatbot"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "chatbot_policy" {
  name        = "ai-bank-chatbot-policy"
  description = "Policy for AI Bank Chatbot"

  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "dynamodb:GetItem",
      "Resource": "${aws_dynamodb_table.database.arn}",
      "Effect": "Allow"
    },
    {
      "Action": "dynamodb:PutItem",
      "Resource": "${aws_dynamodb_table.database.arn}",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "chatbot_attach" {
  role       = aws_iam_role.chatbot_role.name
  policy_arn = aws_iam_policy.chatbot_policy.arn
}

resource "aws_cognito_user_pool" "pool" {
  name                = "ai-bank-chatbot-pool"
  alias              = "ai-bank-chatbot-pool"
  username_attributes = ["email"]
}

resource "aws_cognito_user_pool_client" "client" {
  name            = "ai-bank-chatbot-client"
  user_pool_id   = aws_cognito_user_pool.pool.id
  generate_secret = true
}

# Business Logic
resource "aws_api_gateway_integration" "chatbot_integration" {
  rest_api_id = aws_api_gateway.ui.id
  resource_id = aws_api_gateway_resource.ui_resource.id
  http_method = aws_api_gateway_method.ui_get.http_method
  integration_http_method = "POST"
  type        = "AWS"
  uri         = "arn:aws:apigateway:${aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.chatbot_function.arn}/invocations"
}

# Security Requirements
resource "aws_api_gateway_method_response" "chatbot_response" {
  rest_api_id = aws_api_gateway.ui.id
  resource_id = aws_api_gateway_resource.ui_resource.id
  http_method = aws_api_gateway_method.ui_get.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "chatbot_integration_response" {
  rest_api_id = aws_api_gateway.ui.id
  resource_id = aws_api_gateway_resource.ui_resource.id
  http_method = aws_api_gateway_method.ui_get.http_method
  status_code = aws_api_gateway_method_response.chatbot_response.status_code
  response_templates = {
    "application/json" = ""
  }
}