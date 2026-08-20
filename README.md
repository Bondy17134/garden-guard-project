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

The Compose service uses `restart: unless-stopped`, so Docker starts it again after a crash or server reboot. Images persist in `storage/images`.

Set `INTERESTING_CLASSES` in `.env` to the labels you want. The supplied model has broad COCO labels (such as `bird`, `cat`, and `dog`); it does not identify individual bird species. Set `SHOW_WINDOW=false` on the server.

If RTSP logs show repeated H.264 decoding errors or stream timeouts, set `CAMERA_STREAM=sub` in the server `.env`. The Reolink sub-stream uses less bandwidth and is usually more stable for 24/7 detection. Change it back to `main` only after the main stream is stable.

### Save detections to a Windows PC

A Linux server cannot write directly to a Windows `C:` drive. Share the Windows folder `C:\Users\kunan\OneDrive\Documents\Garden Guard\Detections` as `GardenGuardDetections`, then mount that share on the Linux server. The application writes each image into a date folder such as `19.8.26`.

On Windows, create the folder if needed, then use **Properties → Sharing → Advanced Sharing** to share it. Give your Windows account read/change access. Find the PC's LAN IP address with `ipconfig`.

On the Linux server, install CIFS support and create a protected credentials file:

```bash
sudo apt-get install -y cifs-utils
sudo mkdir -p /mnt/garden-guard-detections
sudo nano /etc/samba/garden-guard-credentials
```

Enter the Windows account details in that credentials file:

```text
username=kunan
password=your-windows-password
domain=WORKGROUP
```

Protect it, then add this line to `/etc/fstab`, replacing `WINDOWS_PC_IP` with the PC's LAN address:

```bash
sudo chmod 600 /etc/samba/garden-guard-credentials
sudo nano /etc/fstab
```

```text
//WINDOWS_PC_IP/GardenGuardDetections /mnt/garden-guard-detections cifs credentials=/etc/samba/garden-guard-credentials,uid=1000,gid=1000,iocharset=utf8,vers=3.0,_netdev,nofail,x-systemd.automount 0 0
```

Mount and test it:

```bash
sudo mount -a
touch /mnt/garden-guard-detections/test-from-linux.txt
```

Set these values in the server's `.env`, then deploy the updated project:

```text
HOST_DETECTIONS_DIR=/mnt/garden-guard-detections
DETECTIONS_DIR=/detections
```

The `test-from-linux.txt` file should appear on the Windows PC before deployment. The next saved visit image will appear under the date folder in the shared Windows Detections folder.

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
