
# Main queue: receives image upload events
resource "aws_sqs_queue" "image_processing" {
  name                       = "garden-guard-image-processing"
  visibility_timeout_seconds = 180
  message_retention_seconds  = 345600 # 4 days

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.image_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Project = "GardenGuard"
    Purpose = "ImageProcessing"
  }
}

# Dead-letter queue: stores messages that repeatedly fail
resource "aws_sqs_queue" "image_dlq" {
  name                      = "garden-guard-image-processing-dlq"
  message_retention_seconds = 1209600 # 14 days

  tags = {
    Project = "GardenGuard"
    Purpose = "FailedImageProcessing"
  }
}

# Only the main queue may use this dead-letter queue
resource "aws_sqs_queue_redrive_allow_policy" "image_dlq" {
  queue_url = aws_sqs_queue.image_dlq.id

  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue"
    sourceQueueArns   = [aws_sqs_queue.image_processing.arn]
  })
}

resource "aws_sqs_queue_policy" "allow_s3" {
  queue_url = aws_sqs_queue.image_processing.id
  policy    = data.aws_iam_policy_document.s3_to_sqs.json
}
