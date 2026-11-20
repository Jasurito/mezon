#!/usr/bin/env bash
# One-time (idempotent) setup of vm1 for Mezon CI/CD. Run as root from a checkout of this repo:
#
#   sudo deploy/vm1/bootstrap.sh "<ssh public key of the CI deploy key>"
#
# Creates: user "deploy" (SSH key restricted, can only sudo /usr/local/sbin/mezon-deploy),
# /opt/mezon/src (rsync target), /etc/mezon/*.env (secrets, generated once, never in git),
# systemd units mezon-db / mezon-backend / mezon-frontend.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PUBKEY="${1:-}"

[ "$(id -u)" -eq 0 ] || { echo "run as root" >&2; exit 1; }

# 1. deploy user
id deploy >/dev/null 2>&1 || useradd --create-home --shell /bin/bash deploy
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
if [ -n "$PUBKEY" ]; then
  # restrict = no pty, no port/agent/X11 forwarding; plain commands and rsync still work
  printf 'restrict %s\n' "$PUBKEY" > /home/deploy/.ssh/authorized_keys
  chown deploy:deploy /home/deploy/.ssh/authorized_keys; chmod 600 /home/deploy/.ssh/authorized_keys
fi

# 2. source dir synced by CI
install -d -m 755 -o deploy -g deploy /opt/mezon /opt/mezon/src

# 3. deploy script (root-owned, so the deploy user cannot change what sudo runs)
install -m 755 -o root -g root "$HERE/mezon-deploy" /usr/local/sbin/mezon-deploy
printf 'deploy ALL=(root) NOPASSWD: /usr/local/sbin/mezon-deploy\n' > /etc/sudoers.d/mezon-deploy
chmod 440 /etc/sudoers.d/mezon-deploy
visudo -cf /etc/sudoers.d/mezon-deploy >/dev/null

# 4. secrets / config (created once; edit by hand later)
install -d -m 750 /etc/mezon
if [ ! -f /etc/mezon/db.env ]; then
  pw="$(openssl rand -hex 24)"
  printf 'POSTGRES_USER=mezon\nPOSTGRES_PASSWORD=%s\nPOSTGRES_DB=mezon\n' "$pw" > /etc/mezon/db.env
  chmod 600 /etc/mezon/db.env
fi
if [ ! -f /etc/mezon/backend.env ]; then
  pw="$(sed -n 's/^POSTGRES_PASSWORD=//p' /etc/mezon/db.env)"
  { printf 'DATABASE_URL=postgresql+psycopg://mezon:%s@mezon-db:5432/mezon\n' "$pw"; cat "$HERE/env/backend.env.example"; } > /etc/mezon/backend.env
  chmod 600 /etc/mezon/backend.env
fi
[ -f /etc/mezon/frontend.build.env ] || install -m 644 "$HERE/env/frontend.build.env.example" /etc/mezon/frontend.build.env

# 5. systemd units
install -m 644 "$HERE"/systemd/mezon-*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable mezon-db.service mezon-backend.service mezon-frontend.service >/dev/null
systemctl start mezon-db.service

echo "bootstrap done. Next: CI rsyncs the repo to /opt/mezon/src and runs 'sudo mezon-deploy all'."
