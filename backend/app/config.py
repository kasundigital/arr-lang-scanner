from __future__ import annotations

import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "config.ini"

_config = configparser.ConfigParser()
if not CONFIG_PATH.exists():
    raise RuntimeError(f"Config file not found: {CONFIG_PATH}")

if not _config.read(CONFIG_PATH):
    raise RuntimeError(f"Failed to read config file: {CONFIG_PATH}")

def _get(section: str, option: str, fallback: str | None = None) -> str | None:
    if _config.has_option(section, option):
        return _config.get(section, option).strip()
    return fallback

SONARR_URL: str = _get("sonarr", "url", "") or ""
SONARR_API_KEY: str = _get("sonarr", "api_key", "") or ""

RADARR_URL: str = _get("radarr", "url", "") or ""
RADARR_API_KEY: str = _get("radarr", "api_key", "") or ""

AUTH_USERNAME: str = _get("auth", "username", "admin")
AUTH_PASSWORD: str = _get("auth", "password", "changeme123")
AUTH_TOKEN: str = _get("auth", "token", "sr-lang-token-change-me")

REQUEST_TIMEOUT: int = int(_get("app", "request_timeout", "60"))
BIND_IP: str = _get("app", "bind_ip", "0.0.0.0")
PORT: int = int(_get("app", "port", "8100"))
LOG_LEVEL: str = _get("app", "log_level", "info")
SERVICE_NAME: str = _get("app", "service_name", "sr-lang-scanner")
