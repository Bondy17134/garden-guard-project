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

## GitHub Actions deployment

The workflow validates Python, builds the container, then deploys only pushes to `main`. Deployment uses a self-hosted GitHub Actions runner on the home server, so no SSH port forwarding or public server address is needed.

Install a Linux self-hosted runner from **GitHub repository Settings → Actions → Runners → New self-hosted runner**. Register it with the `garden-guard` label, run it as a service, and ensure its Linux user can run Docker (`docker ps` must work without `sudo`). Add this GitHub repository variable:

| Variable | Example |
| --- | --- |
| `HOME_SERVER_DEPLOY_PATH` | `/home/bond/garden-guard` |

The deployment path must already contain a populated `.env` file. Each successful push to `main` copies the release files there and restarts the Compose service.
