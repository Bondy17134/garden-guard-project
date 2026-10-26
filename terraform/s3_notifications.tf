# Grant this S3 bucket permission to publish messages
# to the Garden Guard processing queue

data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "s3_to_sqs" {
  statement {
    sid    = "AllowGardenGuardS3Event"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }

    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.image_processing.arn]

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = [aws_s3_bucket.garden_guard.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

# Send image-upload events into SQS
resource "aws_s3_bucket_notification" "images_to_sqs" {
  bucket = aws_s3_bucket.garden_guard.id

  queue {
    id            = "garden-guard-image-uploads"
    queue_arn     = aws_sqs_queue.image_processing.arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "images/"
  }

  depends_on = [aws_sqs_queue_policy.allow_s3]
}