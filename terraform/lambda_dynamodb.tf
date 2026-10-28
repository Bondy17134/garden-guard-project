# Give Lambda DynamoDB permissions

data "aws_iam_policy_document" "lambda_dynamodb" {
  statement {
    sid = "WriteImageMetadata"
    effect = "Allow"

    actions = [ "dynamodb:PutItem" ]

    resources = [ aws_dynamodb_table.image_metadata.arn ]
  }
}

resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "garden-guard-lambda-dynamodb"
  role = aws_iam_role.image_processor.id
  policy = data.aws_iam_policy_document.lambda_dynamodb.json
}