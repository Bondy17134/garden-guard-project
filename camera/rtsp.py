import cv2
import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

username = quote(os.getenv("CAMERA_USERNAME"))
password = quote(os.getenv("CAMERA_PASSWORD"))  
camera_ip = os.getenv("CAMERA_IP")

if not all([username, password, camera_ip]):
    raise ValueError("Missing camera credentials or IP address in .env file.")

rtsp = f"rtsp://{username}:{password}@{camera_ip}:554/h264Preview_01_main"

cap = cv2.VideoCapture(rtsp)

if not cap.isOpened():
    raise RuntimeError("Failed to open RTSP stream. Please check the camera credentials and IP address.")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()