#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-autopost.chezsuzette.sg}"
LE_EMAIL="${2:-support@axon.com.sg}"
APP_DIR="/var/www/${DOMAIN}"
REPO="https://github.com/amitaxonsg/autopost.git"
SERVICE_NAME="autopost"
WORKER_NAME="autopost-worker"

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root: sudo bash scripts/deploy_ubuntu.sh ${DOMAIN} ${LE_EMAIL}"
  exit 1
fi

apt-get update
apt-get install -y python3 python3-venv python3-pip nginx certbot python3-certbot-nginx git

if [ ! -d "${APP_DIR}/.git" ]; then
  mkdir -p "${APP_DIR}"
  git clone "${REPO}" "${APP_DIR}"
else
  git -C "${APP_DIR}" pull --ff-only
fi

cd "${APP_DIR}"
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

mkdir -p instance logs
if [ ! -f .env ]; then
  cp .env.example .env
  SECRET=$(./venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(48))')
  FERNET=$(./venv/bin/python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')
  sed -i "s|^FLASK_SECRET_KEY=.*|FLASK_SECRET_KEY=${SECRET}|" .env
  sed -i "s|^CREDENTIAL_ENCRYPTION_KEY=.*|CREDENTIAL_ENCRYPTION_KEY=${FERNET}|" .env
  echo
  echo "IMPORTANT: Edit ${APP_DIR}/.env now and set ADMIN_EMAIL and ADMIN_PASSWORD."
fi

chown -R www-data:www-data "${APP_DIR}"
chmod 750 "${APP_DIR}"
chmod 640 "${APP_DIR}/.env"

cat >/etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=AutoPost WebUI
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/gunicorn --workers 1 --bind 127.0.0.1:8000 --timeout 120 wsgi:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

cat >/etc/systemd/system/${WORKER_NAME}.service <<EOF
[Unit]
Description=AutoPost Scheduling Worker
After=network.target ${SERVICE_NAME}.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${APP_DIR}/venv/bin/python worker.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat >/etc/nginx/sites-available/${DOMAIN} <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};

    client_max_body_size 5M;

    location /static/ {
        alias ${APP_DIR}/static/;
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 180;
    }
}
EOF

ln -sf /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/${DOMAIN}
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl daemon-reload
systemctl enable --now ${SERVICE_NAME} ${WORKER_NAME}
systemctl reload nginx

echo
echo "HTTP deployment complete."
echo "Check first: curl -I http://${DOMAIN}/healthz"
echo
echo "When DNS resolves correctly, enable SSL with:"
echo "certbot --nginx -d ${DOMAIN} --email ${LE_EMAIL} --agree-tos --no-eff-email --redirect"
echo
echo "After SSL, check:"
echo "systemctl status ${SERVICE_NAME} --no-pager"
echo "systemctl status ${WORKER_NAME} --no-pager"
echo "certbot renew --dry-run"
