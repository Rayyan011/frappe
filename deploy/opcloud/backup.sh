#!/bin/bash
set -euo pipefail
umask 077
cd /opt/stackable-opcloud
exec 9>/run/lock/opcloud-backup.lock
flock -n 9
docker compose -f opcloud-compose.yaml exec -T backend \
  bench --site opcloud.amplii.online backup --with-files
docker compose -f opcloud-compose.yaml exec -T backend env/bin/python -c \
  'from pathlib import Path; p=Path("sites/opcloud.amplii.online/private/backups"); p.chmod(0o700); [f.chmod(0o600) for f in p.iterdir() if f.is_file()]'
