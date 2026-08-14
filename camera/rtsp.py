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

HOME_SERVER_HOST = "192.168.0.237"
HOME_SERVER_USER = "bond"
HOME_SERVER_KEY = r"C:\Users\kunan\.ssh\id_ed25519"
HOME_SERVER_FOLDER = "/home/bond/data/garden-guard/images"

snapshots_dir = project_dir / "storage" / "images"
snapshots_dir.mkdir(parents=True, exist_ok=True)

last_saved = 0
SAVE_COOLDOWN_SECONDS = 30
INTERESTING_CLASSES = {"bird"}

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

        
        for box in results[0].boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            confidence = float(box.conf[0])

            if (
                label in INTERESTING_CLASSES
                and confidence >= 0.65
                and time.time() - last_saved >= SAVE_COOLDOWN_SECONDS
            ):
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = snapshots_dir / f"{timestamp}_{label}_{confidence:.2f}.jpg"

                cv2.imwrite(str(filename), frame)
                print(f"Saved locally: {filename}")

                try:
                    transport = paramiko.Transport((HOME_SERVER_HOST, 22))
                    private_key = paramiko.Ed25519Key.from_private_key_file(HOME_SERVER_KEY)
                    transport.connect(username=HOME_SERVER_USER, pkey=private_key)

                    sftp = paramiko.SFTPClient.from_transport(transport)
                    remote_file = f"{HOME_SERVER_FOLDER}/{filename.name}"
                    sftp.put(str(filename), remote_file)

                    sftp.close()
                    transport.close()

                    print(f"Copied to home server: {remote_file}")

                except Exception as error:
                    print(f"Home-server upload failed: {error}")

                last_saved = time.time()
                break

        annotated_frame = results[0].plot()

        cv2.imshow("Camera — YOLO", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.stop()
    cv2.destroyAllWindows()