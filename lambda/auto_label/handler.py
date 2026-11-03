import json
import os
from functools import lru_cache

import boto3
from roboflow import Roboflow

secrets_client = boto3.client("secretsmanager")

""" 
lru_cache is used to cache the results of the lambda_handler function for up to 4 unique batch_id values.
This is useful for performance optimization, as it avoids repeated calls to the Roboflow API for the same batch_id within the cache limit.
"""
@lru_cache(maxsize=4)
def get_secret(secret_id):
    response = secrets_client.get_secret_value(
        SecretId=secret_id
    )
    return response["SecretString"]

""" Handle the Lambda event for auto-labeling images using Roboflow's API """
def lambda_handler(event, context):
    batch_id = event["batch_id"]

    api_key = get_secret(os.environ["ROBOFLOW_API_KEY"])
    workspace_id = os.environ["ROBOFLOW_WORKSPACE"]
    project_id = os.environ["ROBOFLOW_PROJECT"]
    model_id = os.environ["ROBOFLOW_MODEL_ID"]

    rf = Roboflow(api_key=api_key)

    workspace = rf.workspace(workspace_id)
    project = workspace.project(project_id)
    
    job = project.autolabel(
        batch_id=batch_id,
        model=model_id,
        model_type="foundational",
        ontology={
            "Australian brush turkey, dark bird with red head":
                "bush_turkey",
            "Australian possum": "possum",
            "human person": "person",
        },
        existing_annotations="preserve",
    )

    return{
        "statusCode": 202,
        "body": json.dumps({
            "job_id":job["jobId"],
            "annotation_job_id": job.get("annotationJobId"),
            "status": "SUBMITTED",
        }),
    }