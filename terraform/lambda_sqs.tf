# Least-priviledge access to the processing queue
data "aws_iam_policy_document" "lambda_sqs" {
  statement {
    sid    = "ConsumeGardenGuardMessages"
    effect = "Allow"

    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]

    resources = [
      aws_sqs_queue.image_processing.arn
    ]
  }
}

resource "aws_iam_role_policy" "lambda_sqs" {
  name   = "garden-guard-lambda-sqs"
  role   = aws_iam_role.image_processor.id
  policy = data.aws_iam_policy_document.lambda_sqs.json
}

# Connect SQS to the existing Lambda function
resource "aws_lambda_event_source_mapping" "image_processing" {
  event_source_arn = aws_sqs_queue.image_processing.arn
  function_name    = aws_lambda_function.image_processor.arn

  batch_size = 1
  enabled    = true

  depends_on = [
    aws_iam_role_policy.lambda_sqs
  ]
}