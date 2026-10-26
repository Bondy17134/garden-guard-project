import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Garden Guard Lambda invoked")
    logger.info("Event: %s", json.dump(event))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Garden Guard image processor is working"
        })
    }