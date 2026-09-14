# arr-lang-scanner

A lightweight web dashboard for inspecting audio languages in media managed by **Sonarr** and **Radarr**.

## Easiest Docker setup

The published image is:

```text
ghcr.io/kasundigital/arr-lang-scanner:latest
```

Run it with persistent settings storage:

```bash
docker run -d \
  --name arr-lang-scanner \
  --restart unless-stopped \
  -p 8100:8100 \
  --add-host=host.docker.internal:host-gateway \
  -v arr-lang-scanner-data:/app/data \
  ghcr.io/kasundigital/arr-lang-scanner:latest
```

Then open:

```text
http://SERVER-IP:8100/
```

On first launch the web UI asks you to create the administrator username and password. After that, open **Settings** and add Sonarr/Radarr servers. No API keys or login credentials are required in the Docker command.

## Docker Compose

```bash
mkdir -p arr-lang-scanner && cd arr-lang-scanner
curl -fsSLO https://raw.githubusercontent.com/kasundigital/arr-lang-scanner/main/docker-compose.yml
docker compose up -d
```

The named Docker volume `arr-lang-scanner-data` stores the SQLite settings database, so your servers, API keys and login survive container upgrades.

Update later with:

```bash
docker compose pull
docker compose up -d
```

## Web settings

The Settings page supports:

- multiple Sonarr instances
- multiple Radarr instances
- server name, URL and API key
- connection testing
- edit/delete servers
- administrator username/password changes
- persistent settings stored in SQLite

If Sonarr or Radarr runs directly on the same Linux Docker host, use URLs such as:

```text
http://host.docker.internal:8989
http://host.docker.internal:7878
```

If the Arr applications run on a shared Docker network, use their Docker service/container names instead.

## Optional bootstrap environment variables

New installs do not need these. They remain available for migration or unattended bootstrap:

```text
ARR_USERNAME
ARR_PASSWORD
SONARR_URL
SONARR_API_KEY
RADARR_URL
RADARR_API_KEY
REQUEST_TIMEOUT
ARR_PORT
```

Existing environment values are imported into the persistent settings database when appropriate.

## Features

- Search TV shows from Sonarr and movies from Radarr
- Select the Sonarr/Radarr instance to search
- Aggregate audio-language counts for a selected title
- Season and episode breakdown for Sonarr series
- Clear visual status for English-only, mixed-language, non-English, missing-file, and missing-language cases
- Browser-managed setup and settings
- FastAPI backend and built-in responsive UI
- Password hashing and bearer-token authentication
- Ready-to-run Docker images for `amd64` and `arm64`
- Health endpoint at `/health`
- API documentation at `/api/docs`

## Default ports

- Sonarr: `8989`
- Radarr: `7878`
- arr-lang-scanner: `8100`

## API behavior

Login:

```text
POST /api/login
```

Protected endpoints use:

```text
Authorization: Bearer <token>
```

Core endpoints include:

```text
GET /api/instances
POST /api/instances
POST /api/instances/{id}/test
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

API keys are stored server-side in the persistent SQLite database and are masked in the browser settings list. Passwords are stored as PBKDF2 hashes. Changing the administrator login rotates the active bearer token and requires a new login.

Do not expose the application directly to the public internet without HTTPS and suitable firewall/reverse-proxy protection.

## Container publishing

Every push to `main` automatically builds and publishes `ghcr.io/kasundigital/arr-lang-scanner:latest`. Version tags beginning with `v` are also published. The workflow builds `linux/amd64` and `linux/arm64` images.

## Author

Created by **Kasun Indika (KasunDigital)**

- GitHub: https://github.com/kasundigital
- LinkedIn: https://www.linkedin.com/in/kasundigital/

## License

MIT — see [LICENSE](LICENSE).
