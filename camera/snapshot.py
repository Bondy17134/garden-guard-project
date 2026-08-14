from datetime import datetime, time
from pyexpat import model

import cv2


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
        print(f"Saved: {filename}")

        last_saved = time.time()
        break