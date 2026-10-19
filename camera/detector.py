import os
import torch 
from ultralytics import YOLO 

""" loads YOLO and returns relevant detections """

YOLO_DEVICE = os.getenv("YOLO_DEVICE", "0")

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