#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="config.ini"

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root: sudo ./install.sh"
  exit 1
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  if [[ -f "config.example.ini" ]]; then
    cp config.example.ini "$CONFIG_FILE"
    echo "Created config.ini from config.example.ini. Edit it, then run the installer again."
  else
    echo "config.ini not found in current directory."
  fi
  exit 1
fi

get_ini_value() {
  local section="$1"
  local key="$2"
  awk -F' *= *' -v section="$section" -v key="$key" '
    $0 == "[" section "]" {in_section=1; next}
    /^\[/ {in_section=0}
    in_section && $1 == key {print $2; exit}
  ' "$CONFIG_FILE"
}

set_ini_value() {
  local section="$1"
  local key="$2"
  local value="$3"
  python3 - "$CONFIG_FILE" "$section" "$key" "$value" <<'PY'
import configparser
import sys

path, section, key, value = sys.argv[1:]
cfg = configparser.ConfigParser()
cfg.read(path)
if not cfg.has_section(section):
    cfg.add_section(section)
cfg.set(section, key, value)
with open(path, "w", encoding="utf-8") as f:
    cfg.write(f)
PY
}

SERVICE_NAME="$(get_ini_value app service_name)"
SERVICE_NAME="${SERVICE_NAME:-arr-lang-scanner}"
BIND_IP="$(get_ini_value app bind_ip)"
BIND_IP="${BIND_IP:-0.0.0.0}"
PORT="$(get_ini_value app port)"
PORT="${PORT:-8100}"
AUTH_PASSWORD="$(get_ini_value auth password)"
AUTH_TOKEN="$(get_ini_value auth token)"

if [[ -z "$AUTH_PASSWORD" || "$AUTH_PASSWORD" == "CHANGE_ME" || "$AUTH_PASSWORD" == "changeme123" ]]; then
  echo "ERROR: Set a strong [auth] password in config.ini before installing."
  exit 1
fi

if [[ -z "$AUTH_TOKEN" || "$AUTH_TOKEN" == "CHANGE_ME_RANDOM_TOKEN" || "$AUTH_TOKEN" == "arr-lang-token-change-me" || "$AUTH_TOKEN" == "sr-lang-token-change-me" ]]; then
  GENERATED_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')"
  set_ini_value auth token "$GENERATED_TOKEN"
  echo "Generated a strong random API token in config.ini."
fi

APP_DIR="/opt/$SERVICE_NAME"
LOG_DIR="/var/log/$SERVICE_NAME"
BACKEND_DIR="$APP_DIR/backend"
PYTHON_BIN="python3"
SVC_USER="${SUDO_USER:-root}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is not installed."
  exit 1
fi

if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "Python venv support is missing. Install python3-venv and try again."
  exit 1
fi

echo "Installing $SERVICE_NAME for user: $SVC_USER"
echo "Target directory: $APP_DIR"
echo "Bind IP: $BIND_IP"
echo "Port: $PORT"

mkdir -p "$APP_DIR" "$LOG_DIR"
cp -R . "$APP_DIR"
rm -rf "$APP_DIR/.git" || true
chmod 600 "$APP_DIR/config.ini"
chown -R "$SVC_USER":"$SVC_USER" "$APP_DIR" "$LOG_DIR"

cd "$BACKEND_DIR"
$PYTHON_BIN -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=Sonarr/Radarr Audio Language Scanner
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$SVC_USER
Group=$SVC_USER
WorkingDirectory=$BACKEND_DIR
Environment=PYTHONUNBUFFERED=1
Environment=ARR_LANG_SCANNER_CONFIG=$APP_DIR/config.ini
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host $BIND_IP --port $PORT
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
StandardOutput=append:$LOG_DIR/app.log
StandardError=append:$LOG_DIR/app.log

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "--------------------------------------------------"
echo "Installation complete."
echo "Service: $SERVICE_NAME"
echo "Log file: $LOG_DIR/app.log"
echo "Open: http://<server-ip>:$PORT/"
echo "Use credentials from $APP_DIR/config.ini [auth]."
echo "--------------------------------------------------"
