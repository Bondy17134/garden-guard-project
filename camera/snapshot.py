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