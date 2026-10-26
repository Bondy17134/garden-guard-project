# Package the Python Lambda code
data "archive_file" "image_processor" {
    type = "zip"
    source_file = "${path.module}/../lambda/image_processor/handler.py"
    output_path = "${path.module}/image_processor.zip"
}

# Allow AWS Lambda to assume this IAM role
data "aws_iam_policy_document" "lambda_assume_role" {
    statement {
      actions = [ "sts:AssumeRole" ]

      principals {
        type = "Service"
        identifiers = [ "lambda.amazonaws.com" ]
      }
    }
}

# Lambda execution role
resource "aws_iam_role" "image_processor" {
    name = "garden-guard-image-processor-role"
    assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# Grant basic CloudWatch Logs permissions
resource "aws_iam_role_policy_attachment" "lambda_logging" {
  role       = aws_iam_role.image_processor.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function
resource "aws_lambda_function" "image_processor" {
    function_name = "garden-guard-image-processor"

    filename = data.archive_file.image_processor.output_path
    source_code_hash = data.archive_file.image_processor.output_base64sha256

    role = aws_iam_role.image_processor.arn
    handler = "handler.lambda_handler"
    runtime = "python3.13"

    timeout = 30
    memory_size = 128

    depends_on = [ aws_iam_role_policy_attachment.lambda_logging ]

    tags = {
      Project = "GardenGuard"
      Sprint = "Sprint1" 
    }
}

# Manage Lambda log retention
resource "aws_cloudwatch_log_group" "image_processor" {
  name              = "/aws/lambda/garden-guard-image-processor"
  retention_in_days = 7

  tags = {
    Project = "GardenGuard"
  }
}