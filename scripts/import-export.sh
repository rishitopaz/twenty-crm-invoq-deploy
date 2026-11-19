#!/usr/bin/env bash
# scripts/import-export.sh <twenty-export-*.enc> [crm-hostname]
# Run on the NEW server, from the repo root, after scripts/setup-ubuntu.sh. Turns the encrypted export made by
# scripts/export-from-laptop.sh into a running CRM with exactly the same data, users, workflows and API keys.
#   1. asks the passphrase, opens the export into ./import (private)
#   2. writes .env: same APP_SECRET / ENCRYPTION_KEY as the laptop, same Twenty version, new database password,
#      hostname crm.<server-ip>.sslip.io unless you pass one
#   3. starts Postgres, loads the database, starts Twenty + Caddy (HTTPS), puts the uploaded files back
#   4. compares row counts table by table with the laptop, then deletes the unencrypted copy
# Safe to stop at any point before step 3; refuses to run if .env already exists (FORCE=1 to overwrite a failed try).
set -euo pipefail
cd "$(dirname "$0")/.."
fail() { echo; echo "STOPPED: $*"; exit 1; }
enc="${1:-}"; [ -f "$enc" ] || fail "usage: scripts/import-export.sh <twenty-export-*.enc> [crm-hostname]"
docker compose version >/dev/null 2>&1 || fail "docker compose not available (run: sudo bash scripts/setup-ubuntu.sh, then log out and in)"
[ ! -f .env ] || [ "${FORCE:-0}" = "1" ] || fail ".env already exists: this server is already set up (FORCE=1 to redo a failed import)"
dc="docker compose --env-file .env"

echo "== 1/5 open the export"
rm -rf import; mkdir -m 700 import
read -r -s -p "Passphrase of the export: " pass; echo
PASSX="$pass" openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -pass env:PASSX -in "$enc" | tar -C import -xzf - \
  || fail "wrong passphrase or damaged file"
unset pass
for f in twenty-db.sql.gz files.tgz secrets.env version.txt row-counts.txt; do [ -s "import/$f" ] || fail "import/$f missing in the export"; done
cat import/version.txt

sec() { grep -E "^$1=" import/secrets.env | tail -1 | cut -d= -f2-; }
ver=$(grep -E '^app_version=' import/version.txt | cut -d= -f2-)
[ -n "$ver" ] || ver=$(grep -E '^server_package_version=' import/version.txt | cut -d= -f2-)
ver="${TAG:-$ver}"; [ -n "$ver" ] || fail "cannot tell the Twenty version from version.txt: run again with TAG=vX.Y.Z"
case "$ver" in v*) ;; *) ver="v$ver" ;; esac

echo "== 2/5 write .env (values not shown)"
# Re-run on a server that already has a database (FORCE=1): Postgres keeps the password it was created with,
# so reuse it (and the hostname and sign-up setting), or Twenty could not log in to its own database.
old() { [ -f .env ] && grep -E "^$1=" .env | tail -1 | cut -d= -f2- || true; }
pgpass=$(old PG_DATABASE_PASSWORD); [ -n "$pgpass" ] || pgpass=$(openssl rand -hex 24)
signup=$(old IS_SIGN_UP_DISABLED); [ -n "$signup" ] || signup=true
host="${2:-$(old CRM_HOST)}"
if [ -z "$host" ]; then
  ip=$(curl -s -m 5 -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip || true)
  [ -n "$ip" ] || ip=$(curl -s -m 5 https://api.ipify.org || true)
  [ -n "$ip" ] || fail "cannot find this server's public IP: pass the hostname as the second argument"
  host="crm.${ip//./-}.sslip.io"
fi
umask 077
cat > .env <<EOF
CRM_HOST=$host
TAG=$ver
PG_DATABASE_PASSWORD=$pgpass
APP_SECRET=$(sec APP_SECRET)
ENCRYPTION_KEY=$(sec ENCRYPTION_KEY)
FALLBACK_ENCRYPTION_KEY=$(sec FALLBACK_ENCRYPTION_KEY)
IS_SIGN_UP_DISABLED=$signup
EOF
unset pgpass
umask 022
[ -n "$(sec ENCRYPTION_KEY)" ] || fail "ENCRYPTION_KEY is empty in the export"
echo "hostname: $host   version: $ver"

echo "== 3/5 images and database"
$dc pull -q
want=$(grep -E '^image_digest=' import/version.txt | cut -d= -f2- | grep -o 'sha256:[0-9a-f]*' | head -1 || true)
have=$(docker image inspect -f '{{join .RepoDigests " "}}' "twentycrm/twenty:$ver" | grep -o 'sha256:[0-9a-f]*' | head -1 || true)
if [ -n "$want" ] && [ "$want" != "$have" ]; then echo "WARNING: image digest differs from the laptop ($want vs $have): same tag, different build"; fi
$dc stop server worker >/dev/null 2>&1 || true   # nothing may write to the database while it is replaced
$dc up -d --wait db redis
$dc exec -T redis redis-cli FLUSHALL >/dev/null    # old cache and queued jobs belong to the old data
$dc exec -T db psql -U postgres -d postgres -v ON_ERROR_STOP=1 -q -c 'DROP DATABASE IF EXISTS "default" WITH (FORCE)' -c 'CREATE DATABASE "default"'
gzip -dc import/twenty-db.sql.gz | $dc exec -T db psql -U postgres -d default -v ON_ERROR_STOP=1 -q -o /dev/null
echo "database loaded"

echo "== 4/5 start Twenty and HTTPS"
$dc up -d
echo -n "waiting for the server to be healthy"
for _ in $(seq 1 120); do [ "$($dc ps server --format '{{.Health}}')" = "healthy" ] && break; echo -n .; sleep 5; done; echo
[ "$($dc ps server --format '{{.Health}}')" = "healthy" ] || fail "server not healthy after 10 minutes: $dc logs server --tail 50"
$dc exec -T server tar -C /app/packages/twenty-server -xzf - < import/files.tgz
echo "uploaded files restored"

echo "== 5/5 compare with the laptop"
$dc exec -T db psql -U postgres -d default -At -c "SELECT format('SELECT %L || ''='' || count(*) FROM %I.%I;', table_schema||'.'||table_name, table_schema, table_name) FROM information_schema.tables WHERE table_type='BASE TABLE' AND (table_schema LIKE 'workspace_%' OR table_schema='core') ORDER BY 1" \
  | $dc exec -T db psql -U postgres -d default -At | tr -d '\r' > import/row-counts-cloud.txt
if diff <(grep '^workspace_' import/row-counts.txt) <(grep '^workspace_' import/row-counts-cloud.txt) >/dev/null; then
  echo "DATA IDENTICAL: all $(grep -c '^workspace_' import/row-counts.txt) workspace tables have the same row counts as the laptop"
else
  echo "DIFFERENCES in workspace tables (laptop < > cloud):"; diff <(grep '^workspace_' import/row-counts.txt) <(grep '^workspace_' import/row-counts-cloud.txt) || true
fi
diff <(grep '^core\.' import/row-counts.txt) <(grep '^core\.' import/row-counts-cloud.txt) >/dev/null \
  || echo "note: some core (system) tables changed on start (sessions, jobs): normal"
cp import/row-counts.txt import/version.txt . 2>/dev/null || true
rm -rf import
echo
echo "LIVE: https://$host   (the HTTPS certificate can take about a minute on the first visit)"
echo "Log in with the same email and password as on the laptop. API base URL: https://$host/rest"
echo "Keep the .enc file and its passphrase safe: it is your copy of the data as exported."
