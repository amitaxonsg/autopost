#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-autopost.chezsuzette.sg}"
EMAIL="${2:-support@axon.com.sg}"

echo "AutoPost installer has moved to scripts/deploy_ubuntu.sh"
echo "Running deployment for ${DOMAIN}..."
exec bash "$(dirname "$0")/deploy_ubuntu.sh" "${DOMAIN}" "${EMAIL}"
