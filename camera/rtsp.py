import os
from datetime import datetime
import time
import paramiko
import threading
from pathlib import Path
from urllib.parse import quote

# Must be set BEFORE importing cv2.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

import cv2
from dotenv import load_dotenv

# Keep model-library settings and caches inside this project.
project_dir = Path(__file__).resolve().parents[1]
(project_dir / ".matplotlib").mkdir(exist_ok=True)

os.environ.setdefault("YOLO_CONFIG_DIR", str(project_dir))
os.environ.setdefault("MPLCONFIGDIR", str(project_dir / ".matplotlib"))

from ultralytics import YOLO


class LatestFrameCamera:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.frame = None
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._read_frames, daemon=True)
        self.thread.start()

    def _read_frames(self):
        while self.running:
            cap = cv2.VideoCapture(self.stream_url, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            if not cap.isOpened():
                print("Could not connect — retrying in 2 seconds...")
                time.sleep(2)
                continue

            print("RTSP connected using TCP.")

            while self.running:
                ret, frame = cap.read()

                if not ret:
                    print("Stream dropped — reconnecting...")
                    break

                # Replace any old frame with the newest camera frame.
                with self.lock:
                    self.frame = frame

            cap.release()
            time.sleep(2)

    def get_latest_frame(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()

    def stop(self):
        self.running = False
        self.thread.join(timeout=3)


load_dotenv()

username = quote(os.getenv("CAMERA_USERNAME"), safe="")
password = quote(os.getenv("CAMERA_PASSWORD"), safe="")
camera_ip = os.getenv("CAMERA_IP")

if not all([username, password, camera_ip]):
    raise ValueError("Missing camera credentials or IP address in .env file.")

rtsp = f"rtsp://{username}:{password}@{camera_ip}:554/h264Preview_01_main"

model = YOLO("yolo11n.pt")
camera = LatestFrameCamera(rtsp)

try:
    while True:
        frame = camera.get_latest_frame()

        if frame is None:
            time.sleep(0.01)
            continue

        # YOLO works faster on a smaller copy; display remains reasonably clear.
        inference_frame = cv2.resize(frame, (1280, 960))
        results = model(inference_frame, conf=0.75, verbose=False)
        annotated_frame = results[0].plot()

        cv2.imshow("Camera — YOLO", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.stop()
    cv2.destroyAllWindows()