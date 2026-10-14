"""
Responsibility:
    Read / Parse / Validate / Provide every runtime settings
"""
import os
from urllib.parse import quote
from dotenv import load_dotenv


# load setting from a .env file into environment variables 
load_dotenv()

# encode special characters in credentials so they can be used in a URL
username = quote(os.getenv("CAMERA_USERNAME"), safe="")
password = quote(os.getenv("CAMERA_PASSWORD"), safe="")
camera_ip = os.getenv("CAMERA_IP")

# check that the required connection settings are present
if not all([username, password, camera_ip]):
    raise ValueError("Missing camera credentials or IP address in .env file.")
