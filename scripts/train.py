"""Train Garden Guard's species-specific YOLO model."""

import argparse
import os
from pathlib import Path

from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parents[1]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="yolo11n.pt", help="Pretrained YOLO weights.")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="0", help="GPU index, or 'cpu'.")
    return parser.parse_args()


def main():
    args = parse_args()
    os.chdir(PROJECT_DIR)

    data_file = PROJECT_DIR / "dataset" / "garden_animals.yaml"
    if not data_file.exists():
        raise FileNotFoundError(f"Dataset configuration not found: {data_file}")

    model = YOLO(args.model)
    model.train(
        data=str(data_file),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project=str(PROJECT_DIR / "runs"),
        name="garden_animals",
        exist_ok=True,
    )


if __name__ == "__main__":
    main()
