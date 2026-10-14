# loads YOLO and returns relevant detections

# select the camera stream, defaulting to the main stream
camera_stream = os.getenv("CAMERA_STREAM", "main").strip().lower()
if camera_stream not in {"main", "sub"}:
    raise ValueError("CAMERA_STREAM must be 'main' or 'sub'.")

# construct the Reolink RTSP URL using the selected stream
rtsp = f"rtsp://{username}:{password}@{camera_ip}:554/h264Preview_01_{camera_stream}"
print(f"Using Reolink {camera_stream} RTSP stream.")

# All detections live on the Linux server.  The Docker volume maps this path to
# ./storage on the host, so images survive container rebuilds and restarts.
snapshots_dir = Path(
    os.getenv("DETECTIONS_DIR", str(project_dir / "storage" / "detections"))
)
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
                    "best_frame": inference_frame.copy(),
                }
                print(f"Visit started: {best_current_detection['label']}")

            else:
                active_visit["last_seen"] = now

                if best_current_detection["score"] > active_visit["score"]:
                    active_visit["label"] = best_current_detection["label"]
                    active_visit["confidence"] = best_current_detection["confidence"]
                    active_visit["score"] = best_current_detection["score"]
                    active_visit["best_frame"] = inference_frame.copy()

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