import hashlib
import json
import logging
import os
from datetime import datetime, timezone 
from urllib.parse import unquote_plus

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

def lambda_handler(event, context):
    for sqs_record in event.get("Records", []):
        body = json.loads(sqs_record["body"])

        for s3_record in body.get("Records", []):
            bucket = s3_record["s3"]["bucket"]["name"]
            key = unquote_plus(
                s3_record["s3"]["object"]["key"]
            )

            if not key.lower().endswith(IMAGE_EXTENSIONS):
                logger.info("Skipping non-image: %s, key")
                continue

            # Stable identifier for an S3 object key
            image_id = hashlib.sha256(
                f"{bucket}/{key}".encode("utf-8")
            ).hexdigest()

            timestamp = datetime.now(
                timezone.utc
            ).isoformat()

            item = {
                "image_id": image_id,
                "s3_bucket": bucket,
                "s3_key": key,
                "processing_status": "PENDING",
                "annotation_status": "NOT_STARTED",
                "created_at": timestamp,
            }

            try:
                table.put_item(
                    Item=item,
                    ConditionExpression=(
                        "attribute_not_exists(image_id)"
                    ),
                )
                logger.info(
                    "Metadata saved: image_id=%s, key=%s",
                    image_id,
                    key,
                )
            except ClientError as error:
                code = error.response["Error"]["Code"]

                if code == "ConditionCheckFailedException":
                    logger.info("Already recorded: %s", key)
                else:
                    logger.exception("Failed to save metadata")
                    raise

    return {"statusCode": 200,}