import json
import logging
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    for record in event.get("Records", []):
        # The SQS body contains the original S3 event
        body = json.loads(record["body"])

        for s3_record in body.get("Records", []):
            bucket = s3_record["s3"]["bucket"]["name"]
            key = unquote_plus(
                s3_record["s3"]["object"]["key"]
            )

            logger.info(
                "Image uploaded: bucket=%s, key=%s",
                bucket,
                key
            )

    return {
        "statusCode": 200,
        "message": "SQS events processed"
    }