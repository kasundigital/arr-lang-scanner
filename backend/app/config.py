from __future__ import annotations

import configparser
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(os.environ.get("ARR_LANG_SCANNER_CONFIG", BASE_DIR / "config.ini"))

_config = configparser.ConfigParser()
if CONFIG_PATH.exists():
    if not _config.read(CONFIG_PATH):
        raise RuntimeError(f"Failed to read config file: {CONFIG_PATH}")


def _get(
    section: str,
    option: str,
    fallback: str | None = None,
    env_name: str | None = None,
) -> str | None:
    if env_name:
        env_value = os.environ.get(env_name)
        if env_value is not None and env_value.strip():
            return env_value.strip()
    if _config.has_option(section, option):
        return _config.get(section, option).strip()
    return fallback


def _required(
    section: str,
    option: str,
    env_name: str | None = None,
) -> str:
    value = _get(section, option, "", env_name) or ""
    if not value:
        source = f"environment variable {env_name} or " if env_name else ""
        raise RuntimeError(
            f"Missing required configuration: {source}[{section}] {option}"
        )
    return value


SONARR_URL: str = (
    _get("sonarr", "url", "", "SONARR_URL") or ""
).rstrip("/")
SONARR_API_KEY: str = _get(
    "sonarr", "api_key", "", "SONARR_API_KEY"
) or ""

RADARR_URL: str = (
    _get("radarr", "url", "", "RADARR_URL") or ""
).rstrip("/")
RADARR_API_KEY: str = _get(
    "radarr", "api_key", "", "RADARR_API_KEY"
) or ""

AUTH_USERNAME: str = _get(
    "auth", "username", "admin", "ARR_USERNAME"
) or "admin"
AUTH_PASSWORD: str = _required("auth", "password", "ARR_PASSWORD")
AUTH_TOKEN: str = _get("auth", "token", "", "ARR_TOKEN") or secrets.token_urlsafe(48)

if AUTH_PASSWORD in {"changeme123", "CHANGE_ME"}:
    raise RuntimeError(
        "Refusing to start with the default password. Set ARR_PASSWORD or update [auth] password in config.ini."
    )
if AUTH_TOKEN in {
    "sr-lang-token-change-me",
    "arr-lang-token-change-me",
    "CHANGE_ME_RANDOM_TOKEN",
}:
    raise RuntimeError(
        "Refusing to start with the default token. Set ARR_TOKEN or generate a strong [auth] token in config.ini."
    )

REQUEST_TIMEOUT: int = int(
    _get("app", "request_timeout", "60", "REQUEST_TIMEOUT") or "60"
)
BIND_IP: str = _get("app", "bind_ip", "0.0.0.0", "BIND_IP") or "0.0.0.0"
PORT: int = int(_get("app", "port", "8100", "PORT") or "8100")
LOG_LEVEL: str = _get("app", "log_level", "info", "LOG_LEVEL") or "info"
SERVICE_NAME: str = (
    _get("app", "service_name", "arr-lang-scanner", "SERVICE_NAME")
    or "arr-lang-scanner"
)
