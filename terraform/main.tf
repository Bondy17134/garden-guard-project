terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# AWS as a provider
provider "aws" {
  region = "ap-southeast-2"
}

# AWS S3 
resource "aws_s3_bucket" "garden_guard" {
  bucket_prefix = "garden-guard-images-"

  tags = {
    Project   = "GardenGuard"
    ManagedBy = "Terraform"
  }
}

# AWS S3 Policies (blocking public access)
resource "aws_s3_bucket_public_access_block" "garden_guard" {
  bucket = aws_s3_bucket.garden_guard.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
} 