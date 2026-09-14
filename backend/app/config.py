from __future__ import annotations

import configparser
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(os.environ.get("ARR_LANG_SCANNER_CONFIG", BASE_DIR / "config.ini"))

_config = configparser.ConfigParser()
if not CONFIG_PATH.exists():
    raise RuntimeError(f"Config file not found: {CONFIG_PATH}")

if not _config.read(CONFIG_PATH):
    raise RuntimeError(f"Failed to read config file: {CONFIG_PATH}")


def _get(section: str, option: str, fallback: str | None = None) -> str | None:
    if _config.has_option(section, option):
        return _config.get(section, option).strip()
    return fallback


def _required(section: str, option: str) -> str:
    value = _get(section, option, "") or ""
    if not value:
        raise RuntimeError(f"Missing required configuration: [{section}] {option}")
    return value


SONARR_URL: str = (_get("sonarr", "url", "") or "").rstrip("/")
SONARR_API_KEY: str = _get("sonarr", "api_key", "") or ""

RADARR_URL: str = (_get("radarr", "url", "") or "").rstrip("/")
RADARR_API_KEY: str = _get("radarr", "api_key", "") or ""

AUTH_USERNAME: str = _required("auth", "username")
AUTH_PASSWORD: str = _required("auth", "password")
AUTH_TOKEN: str = _required("auth", "token")

if AUTH_PASSWORD in {"changeme123", "CHANGE_ME"}:
    raise RuntimeError("Refusing to start with the default password. Update [auth] password in config.ini.")
if AUTH_TOKEN in {"sr-lang-token-change-me", "arr-lang-token-change-me", "CHANGE_ME_RANDOM_TOKEN"}:
    raise RuntimeError("Refusing to start with the default token. Generate a strong [auth] token in config.ini.")

REQUEST_TIMEOUT: int = int(_get("app", "request_timeout", "60") or "60")
BIND_IP: str = _get("app", "bind_ip", "0.0.0.0") or "0.0.0.0"
PORT: int = int(_get("app", "port", "8100") or "8100")
LOG_LEVEL: str = _get("app", "log_level", "info") or "info"
SERVICE_NAME: str = _get("app", "service_name", "arr-lang-scanner") or "arr-lang-scanner"
