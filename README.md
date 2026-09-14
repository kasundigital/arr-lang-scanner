# arr-lang-scanner

A lightweight web dashboard for inspecting audio languages in media managed by **Sonarr** and **Radarr**.

It helps you quickly find language inconsistencies, missing media files, and titles where MediaInfo does not contain usable audio-language metadata.

## Quick start with Docker

A ready-to-run multi-architecture image is published at:

```text
ghcr.io/kasundigital/arr-lang-scanner:latest
```

If Sonarr and Radarr run on the same Linux Docker host, run:

```bash
docker run -d \
  --name arr-lang-scanner \
  --restart unless-stopped \
  -p 8100:8100 \
  --add-host=host.docker.internal:host-gateway \
  -e SONARR_URL=http://host.docker.internal:8989 \
  -e SONARR_API_KEY=YOUR_SONARR_API_KEY \
  -e RADARR_URL=http://host.docker.internal:7878 \
  -e RADARR_API_KEY=YOUR_RADARR_API_KEY \
  -e ARR_USERNAME=admin \
  -e ARR_PASSWORD='YOUR_STRONG_PASSWORD' \
  ghcr.io/kasundigital/arr-lang-scanner:latest
```

Then open:

```text
http://SERVER-IP:8100/
```

`ARR_TOKEN` is optional for Docker. If it is omitted, the application securely generates an in-memory bearer token at startup.

## Docker Compose

Download the two small configuration files:

```bash
mkdir -p arr-lang-scanner && cd arr-lang-scanner
curl -fsSLO https://raw.githubusercontent.com/kasundigital/arr-lang-scanner/main/docker-compose.yml
curl -fsSLo .env https://raw.githubusercontent.com/kasundigital/arr-lang-scanner/main/.env.example
nano .env
docker compose up -d
```

Set your Sonarr/Radarr API keys and a strong `ARR_PASSWORD` in `.env` before starting.

The Compose file pulls the published image, so no local source build is required. Update later with:

```bash
docker compose pull
docker compose up -d
```

## Docker environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `SONARR_URL` | When using Sonarr | `http://host.docker.internal:8989` in Compose | Sonarr base URL |
| `SONARR_API_KEY` | When using Sonarr | empty | Sonarr API key |
| `RADARR_URL` | When using Radarr | `http://host.docker.internal:7878` in Compose | Radarr base URL |
| `RADARR_API_KEY` | When using Radarr | empty | Radarr API key |
| `ARR_USERNAME` | No | `admin` | Web login username |
| `ARR_PASSWORD` | Yes | none | Web login password |
| `ARR_TOKEN` | No | auto-generated | Bearer token used after login |
| `REQUEST_TIMEOUT` | No | `60` | Upstream request timeout |
| `ARR_PORT` | Compose only | `8100` | Host port exposed by Compose |

If Sonarr/Radarr are in another Docker Compose stack, you can instead attach this container to a shared Docker network and use their service/container names as the URLs.

## Features

- Search TV shows from Sonarr and movies from Radarr
- Aggregate audio-language counts for a selected title
- Season and episode breakdown for Sonarr series
- Clear visual status for English-only, mixed-language, non-English, missing-file, and missing-language metadata cases
- FastAPI backend with a simple built-in web UI
- Protected API access with username/password login and bearer token authentication
- Ready-to-run Docker image for `amd64` and `arm64`
- Docker Compose and systemd installation options
- Health endpoint at `/health`
- Interactive API documentation at `/api/docs`

## Default ports

- Sonarr: `8989`
- Radarr: `7878`
- arr-lang-scanner: `8100`

## Configuration file mode

The application still supports `config.ini` for non-Docker/systemd installations. Start from `config.example.ini`:

```ini
[sonarr]
url = http://localhost:8989
api_key = YOUR_SONARR_API_KEY_HERE

[radarr]
url = http://localhost:7878
api_key = YOUR_RADARR_API_KEY_HERE

[auth]
username = admin
password = CHANGE_ME
token = CHANGE_ME_RANDOM_TOKEN

[app]
bind_ip = 0.0.0.0
port = 8100
request_timeout = 60
log_level = info
service_name = arr-lang-scanner
```

Environment variables take priority over values in `config.ini`.

## Linux / systemd installation

Requirements: Linux with systemd, Python 3.10+, `python3-venv`, and Sonarr and/or Radarr with API access enabled.

```bash
git clone https://github.com/kasundigital/arr-lang-scanner.git
cd arr-lang-scanner
nano config.ini
sudo ./install.sh
```

The installer validates the password, generates a strong bearer token when needed, installs to `/opt/arr-lang-scanner`, creates the virtual environment and systemd service, and logs to `/var/log/arr-lang-scanner/app.log`.

Useful commands:

```bash
systemctl status arr-lang-scanner
sudo systemctl restart arr-lang-scanner
tail -f /var/log/arr-lang-scanner/app.log
```

## API behavior

Login:

```text
POST /api/login
```

Protected endpoints use:

```text
Authorization: Bearer <token>
```

Main endpoints:

```text
GET /api/search
GET /api/languages
GET /api/tv/{series_id}/episodes
```

## Color guide

- Green: English only
- Orange: English plus other languages
- Blue: no English detected
- Red: media file missing
- Grey: file exists but no usable MediaInfo language data is available

## Security notes

Do not expose the application directly to the public internet without HTTPS and appropriate firewall or reverse-proxy protection. Default passwords/tokens are rejected, authentication comparisons use constant-time helpers, and Sonarr/Radarr API keys are kept server-side.

## Container publishing

Every push to `main` automatically builds and publishes the Docker image to GitHub Container Registry. Version tags beginning with `v` are also published as image tags. The workflow builds both `linux/amd64` and `linux/arm64` images.

## Author

Created by **Kasun Indika (KasunDigital)**

- GitHub: https://github.com/kasundigital
- LinkedIn: https://www.linkedin.com/in/kasundigital/

## License

MIT — see [LICENSE](LICENSE).
