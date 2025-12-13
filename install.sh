#!/usr/bin/env bash
set -e

CONFIG_FILE="config.ini"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "config.ini not found in current directory."
  exit 1
fi

# Read service_name, bind_ip, port from config.ini
SERVICE_NAME=$(awk -F' *= *' '/^service_name/ {print $2}' <(awk '/^\[app\]/{flag=1;next} /^\[.*\]/{flag=0} flag' "$CONFIG_FILE"))
if [[ -z "$SERVICE_NAME" ]]; then
  SERVICE_NAME="sr-lang-scanner"
fi

BIND_IP=$(awk -F' *= *' '/^bind_ip/ {print $2}' <(awk '/^\[app\]/{flag=1;next} /^\[.*\]/{flag=0} flag' "$CONFIG_FILE"))
if [[ -z "$BIND_IP" ]]; then
  BIND_IP="0.0.0.0"
fi

PORT=$(awk -F' *= *' '/^port/ {print $2}' <(awk '/^\[app\]/{flag=1;next} /^\[.*\]/{flag=0} flag' "$CONFIG_FILE"))
if [[ -z "$PORT" ]]; then
  PORT="8100"
fi

APP_NAME="$SERVICE_NAME"
APP_DIR="/opt/$APP_NAME"
LOG_DIR="/var/log/$APP_NAME"
BACKEND_DIR="$APP_DIR/backend"
PYTHON_BIN="python3"

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root: sudo ./install.sh"
  exit 1
fi

SVC_USER="${SUDO_USER:-$USER}"
if [[ -z "$SVC_USER" ]]; then
  echo "Could not detect non-root user to run the service."
  exit 1
fi

echo "Installing $APP_NAME for user: $SVC_USER"
echo "Target directory: $APP_DIR"
echo "Bind IP: $BIND_IP"
echo "Port: $PORT"

mkdir -p "$APP_DIR"
cp -R . "$APP_DIR"

rm -rf "$APP_DIR/.git" || true

mkdir -p "$LOG_DIR"
chown -R "$SVC_USER":"$SVC_USER" "$APP_DIR" "$LOG_DIR"

cd "$APP_DIR/backend"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Python is not installed. Please install Python 3."
  exit 1
fi

$PYTHON_BIN -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"

pip install --upgrade pip
pip install -r requirements.txt

SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=Sonarr/Radarr Audio Language Scanner (\${SERVICE_NAME})
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$SVC_USER
Group=$SVC_USER
WorkingDirectory=$BACKEND_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$APP_DIR/venv/bin/uvicorn app.main:app --host $BIND_IP --port $PORT
Restart=on-failure
RestartSec=5
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
echo "Open: http://$BIND_IP:$PORT/"
echo "Use credentials from config.ini [auth] section."
echo "--------------------------------------------------"
