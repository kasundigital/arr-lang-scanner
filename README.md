# arr-lang-scanner

A lightweight web dashboard for inspecting audio languages in media managed by **Sonarr** and **Radarr**.

It helps you quickly find language inconsistencies, missing media files, and titles where MediaInfo does not contain usable audio-language metadata.

## Features

- Search TV shows from Sonarr and movies from Radarr
- Aggregate audio-language counts for a selected title
- Season and episode breakdown for Sonarr series
- Clear visual status for English-only, mixed-language, non-English, missing-file, and missing-language metadata cases
- FastAPI backend with a simple built-in web UI
- Protected API access with username/password login and bearer token authentication
- systemd installer for Linux
- Docker and Docker Compose support
- Health endpoint at `/health`
- Interactive API documentation at `/api/docs`

## Default ports

The standard Arr ports are used in the example configuration:

- Sonarr: `8989`
- Radarr: `7878`
- arr-lang-scanner: `8100`

## Requirements

For the systemd installation:

- Linux with systemd
- Python 3.9+
- `python3-venv`
- Sonarr and/or Radarr with API access enabled

For Docker:

- Docker Engine
- Docker Compose plugin

## Configuration

Start from `config.example.ini` or edit the included `config.ini` before starting the application.

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

### Security requirements

The application refuses to start with the shipped default password or token.

For the systemd installer, set a strong password before running `install.sh`. If the token is still the placeholder value, the installer generates a cryptographically random token automatically.

Do not expose the application directly to the public internet without HTTPS and appropriate firewall/reverse-proxy protection.

## Linux / systemd installation

```bash
git clone https://github.com/kasundigital/arr-lang-scanner.git
cd arr-lang-scanner
nano config.ini
sudo ./install.sh
```

The installer:

- validates that the default password was changed
- generates a strong bearer token when needed
- copies the application to `/opt/arr-lang-scanner`
- protects the installed config file with restrictive permissions
- creates a Python virtual environment
- installs dependencies
- creates and enables `arr-lang-scanner.service`
- writes logs to `/var/log/arr-lang-scanner/app.log`
- applies basic systemd hardening options

Useful commands:

```bash
systemctl status arr-lang-scanner
sudo systemctl restart arr-lang-scanner
tail -f /var/log/arr-lang-scanner/app.log
```

Open:

```text
http://<server-ip>:8100/
```

## Docker Compose

First set a strong password and token in `config.ini`.

If Sonarr or Radarr runs on the Docker host, remember that `localhost` inside the scanner container refers to the scanner container itself. On Linux, this Compose file provides `host.docker.internal`, so you can use addresses such as:

```ini
[sonarr]
url = http://host.docker.internal:8989

[radarr]
url = http://host.docker.internal:7878
```

Then start the service:

```bash
docker compose up -d --build
```

Check it with:

```bash
docker compose ps
docker compose logs -f
```

## API behavior

The login endpoint is:

```text
POST /api/login
```

Protected endpoints require:

```text
Authorization: Bearer <token>
```

Main protected endpoints include:

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

- Same-origin frontend/API operation is used; permissive wildcard CORS is not enabled.
- Default credentials and placeholder tokens are rejected.
- Authentication comparisons use constant-time comparison helpers.
- API keys remain in the local configuration file and are never sent to the browser.
- Keep `config.ini` out of public screenshots, support bundles, and copied logs when it contains real API keys.

## Author

Created by **Kasun Indika (KasunDigital)**

- GitHub: https://github.com/kasundigital
- LinkedIn: https://www.linkedin.com/in/kasundigital/

## License

MIT — see [LICENSE](LICENSE).
