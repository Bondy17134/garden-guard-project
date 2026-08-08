import cv2
import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote

# Keep model-library settings and caches with the project instead of the user's profile.
project_dir = Path(__file__).resolve().parents[1]
(project_dir / ".matplotlib").mkdir(exist_ok=True)
os.environ.setdefault("YOLO_CONFIG_DIR", str(project_dir))
os.environ.setdefault("MPLCONFIGDIR", str(project_dir / ".matplotlib"))

from ultralytics import YOLO

load_dotenv()

username = quote(os.getenv("CAMERA_USERNAME"), safe="")
password = quote(os.getenv("CAMERA_PASSWORD"), safe="")
camera_ip = os.getenv("CAMERA_IP")

if not all([username, password, camera_ip]):
    raise ValueError("Missing camera credentials or IP address in .env file.")

rtsp = f"rtsp://{username}:{password}@{camera_ip}:554/h264Preview_01_main"

# The nano model is a good lightweight starting point for real-time detection.
# It is downloaded once and cached locally on its first use.
model = YOLO("yolo11n.pt")

cap = cv2.VideoCapture(rtsp)

if not cap.isOpened():
    raise RuntimeError("Failed to open RTSP stream. Please check the camera credentials and IP address.")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, conf=0.5, verbose=False)
    annotated_frame = results[0].plot()

    cv2.imshow("Camera — YOLO", annotated_frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
