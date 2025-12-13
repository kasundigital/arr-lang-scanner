# arr-lang-scanner

arr-lang-scanner is a lightweight, fast, and modern web-based scanner for detecting audio languages inside media files managed by Sonarr (TV) and Radarr (Movies).

This tool helps quickly identify language inconsistencies, validate media quality, and manage multi-language libraries with an easy-to-use dashboard.

---

## 🚀 Key Features

• Search TV shows and movies directly via Sonarr/Radarr  
• Detect audio languages from each media file (via MediaInfo)  
• Full season → episode breakdown for TV shows  
• Aggregate audio-language summary for Movies and TV  
• Modern dark UI with color coding  
  - Green = English only  
  - Orange = English + other languages  
  - Blue = No English  
  - Red = File missing  
  - Grey = File exists but no MediaInfo  

All settings are controlled by a single config.ini file.

---

## 📦 Requirements

• Linux server (systemd)  
• Python 3.9 or newer  
• Sonarr and/or Radarr with API enabled  

---

## ⚙️ Configuration (`config.ini`)

Edit this file before installation:

[sonarr]
url = https://sonarr.example.com
api_key = YOUR_SONARR_API_KEY

[radarr]
url = https://radarr.example.com
api_key = YOUR_RADARR_API_KEY

[auth]
username = admin
password = changeme123
token = arr-lang-token-change-me

[app]
bind_ip = 0.0.0.0
port = 8100
request_timeout = 60
log_level = info
service_name = arr-lang-scanner

---

## 📥 Installation

git clone https://github.com/kasundigital/arr-lang-scanner.git
cd arr-lang-scanner

nano config.ini          (update URLs + API keys)

sudo ./install.sh        (sets up service and auto-starts it)

Installer actions:
• Copies project to /opt/arr-lang-scanner  
• Creates virtual environment  
• Installs Python dependencies  
• Generates systemd service “arr-lang-scanner.service”  
• Creates logs in /var/log/arr-lang-scanner/  
• Starts service  

---

## 🖥 Service Commands

Check service:
systemctl status arr-lang-scanner

Restart service:
sudo systemctl restart arr-lang-scanner

View logs:
tail -f /var/log/arr-lang-scanner/app.log

---

## 🌐 Web Interface

Open in browser:

http://<server-ip>:8100/

Login using credentials from:

[auth]
username = ...
password = ...

---

## 🧩 Features Overview

TV Mode (Sonarr):
• Search shows  
• Season listing  
• Per-episode language detection  
• Highlights mismatches visually  

Movie Mode (Radarr):
• Search movies  
• Show all detected audio languages  

---

## 👤 Author

Created by **Kasun Indika (KasunDigital)**  
GitHub: https://github.com/kasundigital  
LinkedIn: https://www.linkedin.com/in/kasundigital/

---

## 📜 License

MIT License. Free to modify and use.

