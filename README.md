# Garden Guard

Garden Guard watches an RTSP camera and stores the best image from each detected animal visit.

## Run continuously on the home server

The server needs Docker Engine with the Compose plugin and access to the RTSP camera on the local network. Enable Docker at boot (`sudo systemctl enable --now docker` on Ubuntu). On the server, create the deployment directory, copy `.env.example` to `.env`, and fill in the camera credentials. Keep `.env` only on the server; it is intentionally excluded from Git and deployments.

```bash
mkdir -p ~/garden-guard
cd ~/garden-guard
cp .env.example .env
docker compose up -d --build
docker compose logs -f
```

The Compose service uses `restart: unless-stopped`, so Docker starts it again after a crash or server reboot. Images persist on the Linux server in `storage/detections`.

Garden Guard keeps detections in a predictable structure, grouped first by date and then by the detected animal:

```text
storage/detections/
  2026/08/21/bird/14-32-09_0.86.jpg
  2026/08/21/cat/20-05-41_0.91.jpg
```

The image filename is the detection time and confidence. This means each day has separate folders for each animal label, making it straightforward to review detections or select images later for training.

Set `INTERESTING_CLASSES` in `.env` to the labels you want. The supplied model has broad COCO labels (such as `bird`, `cat`, and `dog`); it does not identify individual bird species. Set `SHOW_WINDOW=false` on the server.

If RTSP logs show repeated H.264 decoding errors or stream timeouts, set `CAMERA_STREAM=sub` in the server `.env`. The Reolink sub-stream uses less bandwidth and is usually more stable for 24/7 detection. Change it back to `main` only after the main stream is stable.

### NVIDIA GPU

Garden Guard is configured to require GPU `0` (`YOLO_DEVICE=0`). Install the NVIDIA driver and NVIDIA Container Toolkit on the server, then configure Docker and restart it:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify that Docker can access the GPU before deploying:

```bash
docker run --rm --gpus all nvidia/cuda:12.9.0-base-ubuntu22.04 nvidia-smi
```

After deployment, `docker compose logs garden-guard` must report `YOLO is running on GPU:`. If you deliberately run without a GPU, set `YOLO_DEVICE=cpu`; otherwise the service exits rather than silently falling back to CPU.

## Train a species-specific model

The default model recognises broad categories only. To train `bush_turkey` and `possum`, follow the dataset setup in [`dataset/README.md`](dataset/README.md), then train on a GPU-equipped machine:

```bash
python scripts/train.py --epochs 100 --imgsz 960 --device 0
```

The best model is written to `runs/garden_animals/weights/best.pt`. Test it on held-out day and infrared-night footage before making it the live detector.

To temporarily run a locally trained model in the live detector, keep its weights under the server's `runs/` directory and update the server-only `.env` file. For example:

```text
YOLO_MODEL=/app/runs/bush_turkey_v1/weights/best.pt
INTERESTING_CLASSES=bush_turkey
CONFIDENCE_THRESHOLD=0.35
```

Then recreate the service with `docker compose up -d --force-recreate`. The `runs/` directory is mounted read-only into the detector container and is excluded from Git, so the model stays on the server. To switch back to the supplied general model, set `YOLO_MODEL=yolo11n.pt` and restore the broader `INTERESTING_CLASSES` list.

On the GPU home server, run the same training command in the project container after placing the labelled dataset in `dataset/`:

```bash
docker compose run --rm \
  -v ./dataset:/app/dataset \
  -v ./runs:/app/runs \
  garden-guard python scripts/train.py --epochs 100 --imgsz 960 --device 0
```

## GitHub Actions deployment

The workflow validates Python, builds the container, then deploys only pushes to `main`. Deployment uses a self-hosted GitHub Actions runner on the home server, so no SSH port forwarding or public server address is needed.

Install a Linux self-hosted runner from **GitHub repository Settings → Actions → Runners → New self-hosted runner**. Register it with the `garden-guard` label, run it as a service, and ensure its Linux user can run Docker (`docker ps` must work without `sudo`). Add this GitHub repository variable:

| Variable | Example |
| --- | --- |
| `HOME_SERVER_DEPLOY_PATH` | `/home/bond/garden-guard` |

The deployment path must already contain a populated `.env` file. Each successful push to `main` copies the release files there and restarts the Compose service.
