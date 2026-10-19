from pathlib import Path # handle file and folder path
import paramiko # connect to a server using SSH/SFTP
from datetime import datetime # generate timestamps for saved images
import time # track time between snapshots
import cv2 # process and save images using OpenCV

from saving_images import inference_frame
from detector import model

# get the project root (two directory levels about this file)
project_dir = Path(__file__).resolve().parents[1]

# home server connection details
HOME_SERVER_HOST = "192.168.0.237"  
HOME_SERVER_USER = "bond"

# path to the SSH private key on computer
HOME_SERVER_KEY = r"C:\Users\kunan\.ssh\id_ed25519"  # Use your actual private-key path

# destination folder for uploaded images on the home server
HOME_SERVER_FOLDER = "/home/bond/data/garden-guard/images"

# create the local snapshot folder, including missing parent folders
# if the folder already exists, do not raise an error
snapshots_dir = project_dir / "storage" / "images"
snapshots_dir.mkdir(parents=True, exist_ok=True)

# store the time the most recent snapshot was saved
last_saved = 0

# minimum time between saved snapshots, in seconds
SAVE_COOLDOWN_SECONDS = 30

# detection classes that should trigger a snapshot
INTERESTING_CLASSES = {"bird"}

# Run object detection on the prepared frame.
# conf=0.65: keep detections with a confidence score of at least 65%.
# verbose=False: suppress detailed inference logs.
results = model(inference_frame, conf=0.65, verbose=False)
