from __future__ import annotations

import configparser
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(os.environ.get("ARR_LANG_SCANNER_CONFIG", BASE_DIR / "config.ini"))

_config = configparser.ConfigParser()
if CONFIG_PATH.exists() and not _config.read(CONFIG_PATH):
    raise RuntimeError(f"Failed to read config file: {CONFIG_PATH}")


def _get(section: str, option: str, fallback: str | None = None, env_name: str | None = None) -> str | None:
    if env_name:
        env_value = os.environ.get(env_name)
        if env_value is not None and env_value.strip():
            return env_value.strip()
    if _config.has_option(section, option):
        return _config.get(section, option).strip()
    return fallback


REQUEST_TIMEOUT: int = int(_get("app", "request_timeout", "60", "REQUEST_TIMEOUT") or "60")
BIND_IP: str = _get("app", "bind_ip", "0.0.0.0", "BIND_IP") or "0.0.0.0"
PORT: int = int(_get("app", "port", "8100", "PORT") or "8100")
LOG_LEVEL: str = _get("app", "log_level", "info", "LOG_LEVEL") or "info"
SERVICE_NAME: str = _get("app", "service_name", "arr-lang-scanner", "SERVICE_NAME") or "arr-lang-scanner"
