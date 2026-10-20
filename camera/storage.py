# saves image files into date/animal folders

from datetime import datetime
import time
import cv2
from pathlib import Path
import os

# get the project root: the parent of the directory containing this script
project_dir = Path(__file__).resolve().parents[1]

# All detections live on the Linux server.  The Docker volume maps this path to
# ./storage on the host, so images survive container rebuilds and restarts.
snapshots_dir = Path(
    os.getenv("DETECTIONS_DIR", str(project_dir / "storage" / "detections"))
)
snapshots_dir.mkdir(parents=True, exist_ok=True)


def save_visit_image(image, label, confidence):
    global last_saved

    now = datetime.now()
    # Example: storage/detections/2026/08/21/bird/14-32-09_0.86.jpg
    # This makes it easy to browse by year, day, and detected animal.
    date_folder = (
        snapshots_dir
        / f"{now:%Y}"
        / f"{now:%m}"
        / f"{now:%d}"
        / label
    )
    date_folder.mkdir(parents=True, exist_ok=True)
    filename = date_folder / f"{now:%H-%M-%S}_{confidence:.2f}.jpg"

    if not cv2.imwrite(str(filename), image):
        print(f"Could not save visit image: {filename}")
        return

    print(f"Saved best visit image: {filename}")

    last_saved = time.time()