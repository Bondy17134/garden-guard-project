import os 
from roboflow import Roboflow
from dotenv import load_dotenv

load_dotenv()

roboflow_api_key = os.getenv("ROBOFLOW_API_KEY")
roboflow_workspace = os.getenv("ROBOFLOW_WORKSPACE")
roboflow_project = os.getenv("ROBOFLOW_PROJECT")

rf = Roboflow(api_key=roboflow_api_key)
workspace = rf.workspace(roboflow_workspace)
project = workspace.project(roboflow_project)

print("Available Auto Label Models:")
for model in workspace.autolabel_models()["models"]:
    print(
        model["id"],
        "available:", model["available"],
        #"credits/image:", model["CreditPerImage"],
    )

print("\nAvailable batches:")
print(project.get_annotation_batches())