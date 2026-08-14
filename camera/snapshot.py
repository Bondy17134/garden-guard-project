from pathlib import Path
import paramiko
from datetime import datetime
import time
import cv2

project_dir = Path(__file__).resolve().parents[1]

HOME_SERVER_HOST = "192.168.0.237"  
HOME_SERVER_USER = "bond"
HOME_SERVER_KEY = r"C:\Users\kunan\.ssh\id_ed25519"  # Use your actual private-key path
HOME_SERVER_FOLDER = "/home/bond/data/garden-guard/images"

snapshots_dir = project_dir / "storage" / "images"
snapshots_dir.mkdir(parents=True, exist_ok=True)

last_saved = 0
SAVE_COOLDOWN_SECONDS = 30
INTERESTING_CLASSES = {"bird"}

results = model(inference_frame, conf=0.65, verbose=False)
