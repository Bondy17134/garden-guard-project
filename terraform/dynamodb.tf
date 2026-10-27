resource "aws_dynamodb_table" "image_metadata" {
  name = "garden-guard-image-metadata"
  # Pay for actual DynamoDB read/write usage
  billing_mode = "PAY_PER_REQUEST"

  # Defines the primary key for each image
  hash_key = "image_id"

  attribute {
    name = "image_id"
    # Image ID is stored as a string
    type = "S"
  }

  # Encrypts the table data as a string
  server_side_encryption {
    enabled = true
  }

  # For now, keep it simple to avoid the additional backup charge
  point_in_time_recovery {
    enabled = false
  }

  tags = {
    Project     = "GardenGuard"
    Environment = "Development"
    ManagedBy   = "Terraform"
  }
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.image_metadata.name
}