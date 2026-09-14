from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get("ARR_DATA_DIR", "/app/data"))
DB_PATH = DATA_DIR / "settings.db"


def _conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS arr_instances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL CHECK(kind IN ('sonarr','radarr')),
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                api_key TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                UNIQUE(kind, name)
            );
            """
        )
        if not get_setting("auth_token", db=db):
            set_setting("auth_token", secrets.token_urlsafe(48), db=db)

        # Optional one-time bootstrap from Docker environment variables.
        if not is_setup_complete(db=db):
            username = os.environ.get("ARR_USERNAME", "").strip()
            password = os.environ.get("ARR_PASSWORD", "")
            if username and password:
                set_credentials(username, password, db=db)

        _import_env_instance("sonarr", "SONARR_URL", "SONARR_API_KEY", db)
        _import_env_instance("radarr", "RADARR_URL", "RADARR_API_KEY", db)


def _import_env_instance(kind: str, url_var: str, key_var: str, db: sqlite3.Connection) -> None:
    url = os.environ.get(url_var, "").strip().rstrip("/")
    api_key = os.environ.get(key_var, "").strip()
    if not url or not api_key:
        return
    exists = db.execute("SELECT 1 FROM arr_instances WHERE kind=? LIMIT 1", (kind,)).fetchone()
    if not exists:
        db.execute(
            "INSERT INTO arr_instances(kind,name,url,api_key,enabled) VALUES(?,?,?,?,1)",
            (kind, f"Main {kind.title()}", url, api_key),
        )
        db.commit()


def get_setting(key: str, default: str | None = None, db: sqlite3.Connection | None = None) -> str | None:
    owns = db is None
    db = db or _conn()
    try:
        row = db.execute("SELECT value FROM app_settings WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default
    finally:
        if owns:
            db.close()


def set_setting(key: str, value: str, db: sqlite3.Connection | None = None) -> None:
    owns = db is None
    db = db or _conn()
    try:
        db.execute(
            "INSERT INTO app_settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        db.commit()
    finally:
        if owns:
            db.close()


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, rounds, salt_hex, digest_hex = encoded.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(rounds))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False


def set_credentials(username: str, password: str, db: sqlite3.Connection | None = None) -> None:
    if len(username.strip()) < 1:
        raise ValueError("Username is required")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    owns = db is None
    db = db or _conn()
    try:
        set_setting("username", username.strip(), db=db)
        set_setting("password_hash", _hash_password(password), db=db)
    finally:
        if owns:
            db.close()


def is_setup_complete(db: sqlite3.Connection | None = None) -> bool:
    owns = db is None
    db = db or _conn()
    try:
        return bool(get_setting("username", db=db) and get_setting("password_hash", db=db))
    finally:
        if owns:
            db.close()


def list_instances(kind: str | None = None, include_keys: bool = False) -> list[dict[str, Any]]:
    with _conn() as db:
        if kind:
            rows = db.execute("SELECT * FROM arr_instances WHERE kind=? ORDER BY name", (kind,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM arr_instances ORDER BY kind,name").fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["enabled"] = bool(item["enabled"])
        if not include_keys:
            item["api_key"] = "••••••••" if item["api_key"] else ""
        result.append(item)
    return result


def get_instance(instance_id: int, kind: str | None = None) -> dict[str, Any] | None:
    with _conn() as db:
        if kind:
            row = db.execute("SELECT * FROM arr_instances WHERE id=? AND kind=? AND enabled=1", (instance_id, kind)).fetchone()
        else:
            row = db.execute("SELECT * FROM arr_instances WHERE id=? AND enabled=1", (instance_id,)).fetchone()
    return dict(row) if row else None


def save_instance(kind: str, name: str, url: str, api_key: str, enabled: bool = True, instance_id: int | None = None) -> int:
    kind = kind.lower().strip()
    if kind not in {"sonarr", "radarr"}:
        raise ValueError("Invalid instance type")
    name, url, api_key = name.strip(), url.strip().rstrip("/"), api_key.strip()
    if not name or not url or not api_key:
        raise ValueError("Name, URL and API key are required")
    with _conn() as db:
        if instance_id:
            existing = db.execute("SELECT api_key FROM arr_instances WHERE id=?", (instance_id,)).fetchone()
            if not existing:
                raise ValueError("Instance not found")
            if api_key == "••••••••":
                api_key = existing["api_key"]
            db.execute(
                "UPDATE arr_instances SET kind=?,name=?,url=?,api_key=?,enabled=? WHERE id=?",
                (kind, name, url, api_key, int(enabled), instance_id),
            )
            db.commit()
            return instance_id
        cur = db.execute(
            "INSERT INTO arr_instances(kind,name,url,api_key,enabled) VALUES(?,?,?,?,?)",
            (kind, name, url, api_key, int(enabled)),
        )
        db.commit()
        return int(cur.lastrowid)


def delete_instance(instance_id: int) -> None:
    with _conn() as db:
        db.execute("DELETE FROM arr_instances WHERE id=?", (instance_id,))
        db.commit()
