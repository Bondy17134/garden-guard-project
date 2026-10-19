import os
from pathlib import Path
import torch 
from datetime import datetime
import time 
import cv2
from ultralytics import YOLO 

from config import username, password, camera_ip

from stream import LatestFrameCamera

from saving_images import save_visit_image

""" loads YOLO and returns relevant detections """

# select the camera stream, defaulting to the main stream
camera_stream = os.getenv("CAMERA_STREAM", "main").strip().lower()
if camera_stream not in {"main", "sub"}:
    raise ValueError("CAMERA_STREAM must be 'main' or 'sub'.")

YOLO_DEVICE = os.getenv("YOLO_DEVICE", "0")

# construct the Reolink RTSP URL using the selected stream
rtsp = f"rtsp://{username}:{password}@{camera_ip}:554/h264Preview_01_{camera_stream}"
print(f"Using Reolink {camera_stream} RTSP stream.")


# GPU avaibility check
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

save_visit_image