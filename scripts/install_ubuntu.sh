#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${1:-/var/www/autopost.chezsuzette.sg}"

sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER":"$USER" "$APP_DIR"

echo "Clone repository:"
echo "git clone https://github.com/amitaxonsg/autopost.git $APP_DIR"
echo
echo "Then:"
echo "cd $APP_DIR"
echo "python3 -m venv venv"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo "cp .env.example .env"
echo
echo "After editing .env, test with:"
echo "python app.py"
