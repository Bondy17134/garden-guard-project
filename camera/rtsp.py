import os
from datetime import datetime
import time
import threading
from pathlib import Path
from urllib.parse import quote

# Must be set BEFORE importing cv2.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

import cv2
import torch
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

snapshots_dir = project_dir / "storage" / "images"
snapshots_dir.mkdir(parents=True, exist_ok=True)

last_saved = 0
SAVE_COOLDOWN_SECONDS = int(os.getenv("SAVE_COOLDOWN_SECONDS", "30"))
INTERESTING_CLASSES = {
    label.strip()
    for label in os.getenv(
        "INTERESTING_CLASSES",
        "bird,cat,dog,horse,sheep,cow,elephant,bear,zebra,giraffe,person",
    ).split(",")
    if label.strip()
}
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
VISIT_END_SECONDS = float(os.getenv("VISIT_END_SECONDS", "3"))
SHOW_WINDOW = os.getenv("SHOW_WINDOW", "false").lower() == "true"
YOLO_DEVICE = os.getenv("YOLO_DEVICE", "0")
active_visit = None

if YOLO_DEVICE != "cpu" and not torch.cuda.is_available():
    raise RuntimeError(
        "YOLO_DEVICE requests a GPU, but PyTorch cannot access CUDA. "
        "Check the NVIDIA Container Toolkit and Docker GPU configuration."
    )

if YOLO_DEVICE == "cpu":
    print("YOLO is running on CPU.")
else:
    print(f"YOLO is running on GPU: {torch.cuda.get_device_name(0)}")

model = YOLO(os.getenv("YOLO_MODEL", "yolo11n.pt"))
camera = LatestFrameCamera(rtsp)

def save_visit_image(image, label, confidence):
    global last_saved

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = snapshots_dir / f"{timestamp}_{label}_{confidence:.2f}.jpg"

    cv2.imwrite(str(filename), image)
    print(f"Saved best visit image: {filename}")

    last_saved = time.time()

try:
    while True:
        frame = camera.get_latest_frame()

        if frame is None:
            time.sleep(0.01)
            continue

        # YOLO works faster on a smaller copy; display remains reasonably clear.
        inference_frame = cv2.resize(frame, (1280, 960))
        results = model(
            inference_frame,
            conf=CONFIDENCE_THRESHOLD,
            device=YOLO_DEVICE,
            verbose=False,
        )
        annotated_frame = results[0].plot()

        best_current_detection = None

        for box in results[0].boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            confidence = float(box.conf[0])

            if label not in INTERESTING_CLASSES or confidence < CONFIDENCE_THRESHOLD:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            box_area = (x2 - x1) * (y2 - y1)
            score = box_area * confidence

            if (
                best_current_detection is None
                or score > best_current_detection["score"]
            ):
                best_current_detection = {
                    "label": label,
                    "confidence": confidence,
                    "score": score,
                }

        now = time.time()

        if best_current_detection is not None:
            if active_visit is None:
                active_visit = {
                    "last_seen": now,
                    "label": best_current_detection["label"],
                    "confidence": best_current_detection["confidence"],
                    "score": best_current_detection["score"],
                    "best_frame": annotated_frame.copy(),
                }
                print(f"Visit started: {best_current_detection['label']}")

            else:
                active_visit["last_seen"] = now

                if best_current_detection["score"] > active_visit["score"]:
                    active_visit["label"] = best_current_detection["label"]
                    active_visit["confidence"] = best_current_detection["confidence"]
                    active_visit["score"] = best_current_detection["score"]
                    active_visit["best_frame"] = annotated_frame.copy()

        elif (
            active_visit is not None
            and now - active_visit["last_seen"] >= VISIT_END_SECONDS
            and now - last_saved >= SAVE_COOLDOWN_SECONDS
        ):
            print(f"Visit ended: saving best {active_visit['label']} image.")
            save_visit_image(
                active_visit["best_frame"],
                active_visit["label"],
                active_visit["confidence"],
            )
            active_visit = None

        if SHOW_WINDOW:
            cv2.imshow("Camera — YOLO", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    camera.stop()
    cv2.destroyAllWindows()
