"""
Responsibility:
    Read / Parse / Validate / Provide every runtime settings
"""
import os
from urllib.parse import quote
from dotenv import load_dotenv

" 1. Read raw username, password and IP value"
# load setting from a .env file into environment variables 
load_dotenv()

# Declare raw credentials from .env
raw_username = os.getenv("CAMERA_USERNAME")
raw_password = os.getenv("CAMERA_PASSWORD")
raw_camera_ip = os.getenv("CAMERA_IP")

" 2. Confirm none are missing or empty"
if(
    raw_username == None or
    raw_password == None or
    raw_camera_ip == None
   ):
    raise ValueError("Missing camera credentials or IP address in .env file.")

" 3. Run quote() on the valited username and password"
# encode special characters in credentials so they can be used in a URL
username = quote(raw_username, safe="")
password = quote(raw_password, safe="")
camera_ip = raw_camera_ip

" 4. Select camera stream"
# select the camera stream, defaulting to the main stream
camera_stream = os.getenv("CAMERA_STREAM", "main").strip().lower()
if camera_stream not in {"main", "sub"}:
    raise ValueError("CAMERA_STREAM must be 'main' or 'sub'.")

" 5. Build the RTSP URL"
# construct the Reolink RTSP URL using the selected stream
rtsp_url = f"rtsp://{username}:{password}@{camera_ip}:554/h264Preview_01_{camera_stream}"
print(f"Using Reolink {camera_stream} RTSP stream.")