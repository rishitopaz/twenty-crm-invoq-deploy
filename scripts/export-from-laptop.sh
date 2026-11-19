#!/bin/bash
# export-from-laptop.sh   Run on the Mac where Twenty runs today. Makes ONE encrypted file with everything the cloud server needs.
#
#   bash export-from-laptop.sh            (Twenty folder is ~/twenty)
#   bash export-from-laptop.sh /path      (Twenty folder somewhere else)
#
# SAFE: it only READS. It does not stop, change or delete anything in your CRM.
# Output on your Desktop:  twenty-export-<date>.enc  containing
#   twenty-db.sql.gz   full database dump (all objects, records, workflows, roles, users, API keys, settings)
#   files.tgz          uploaded files (attachments, avatars)
#   secrets.env        APP_SECRET, ENCRYPTION_KEY (+ fallback), TAG: without these, logins, API keys and the mailbox break
#   version.txt        the exact Twenty version (the cloud must start on the same one)
#   row-counts.txt     rows per table, to prove the cloud copy is identical
# You type a passphrase (min 12 characters). Send the .enc file by Teams/Drive; say the passphrase by phone/WhatsApp,
# never in the same message as the file. Nothing secret is printed on screen.
set -euo pipefail
export COPYFILE_DISABLE=1   # macOS tar: no ._ metadata files inside the archive
cd "${1:-$HOME/twenty}" || { echo "folder not found: ${1:-$HOME/twenty}"; exit 1; }
fail() { echo; echo "STOPPED: $*"; exit 1; }
[ -f docker-compose.yml ] && [ -f .env ] || fail "run from the Twenty folder (it has docker-compose.yml and .env), or pass it: bash export-from-laptop.sh ~/twenty"
docker info >/dev/null 2>&1 || fail "Docker is not running: open Docker Desktop, wait until it says running, then run this again"
[ "$(docker compose ps server --format '{{.Health}}' 2>/dev/null)" = "healthy" ] || fail "Twenty is not healthy: run 'docker compose up -d', wait 2 minutes, run this again"
openssl enc -help 2>&1 | grep -q pbkdf2 || fail "this openssl has no -pbkdf2 (run: brew install openssl, then try again)"

getenv() { grep -E "^$1=" .env | tail -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//" || true; }
PGU=$(getenv PG_DATABASE_USER); PGU=${PGU:-postgres}
PGD=$(getenv PG_DATABASE_NAME); PGD=${PGD:-default}
stamp=$(date +%Y%m%d-%H%M)
w=$(mktemp -d); trap 'rm -rf "$w"' EXIT; chmod 700 "$w"
dc="docker compose"

echo "== 1/6 version"
sid=$($dc ps -q server)
img=$(docker inspect -f '{{.Config.Image}}' "$sid")
{
  echo "image=$img"
  echo "image_digest=$(docker image inspect -f '{{join .RepoDigests " "}}' "$img" 2>/dev/null)"
  echo "app_version=$($dc exec -T server sh -c 'echo "${APP_VERSION:-}"' | tr -d '\r')"
  echo "server_package_version=$($dc exec -T server sh -c 'node -p "require(\"/app/packages/twenty-server/package.json\").version" 2>/dev/null' | tr -d '\r')"
  echo "postgres=$($dc exec -T db psql -U "$PGU" -d "$PGD" -Atc 'show server_version' | tr -d '\r')"
  echo "exported_at_utc=$(date -u +%FT%TZ)"
} > "$w/version.txt"
cat "$w/version.txt"

echo "== 2/6 database dump"
$dc exec -T db pg_dump -U "$PGU" "$PGD" | gzip > "$w/twenty-db.sql.gz"
gzip -t "$w/twenty-db.sql.gz" || fail "dump archive is broken"
[ "$(gzip -dc "$w/twenty-db.sql.gz" | head -c 300 | grep -c 'PostgreSQL database dump')" -ge 1 ] || fail "dump looks empty"
gzip -dc "$w/twenty-db.sql.gz" | tail -c 300 | grep -q 'PostgreSQL database dump complete' || fail "dump is incomplete"
echo "ok ($(du -h "$w/twenty-db.sql.gz" | cut -f1))"

echo "== 3/6 uploaded files"
$dc exec -T server tar -C /app/packages/twenty-server -czf - .local-storage > "$w/files.tgz"
tar -tzf "$w/files.tgz" >/dev/null || fail "files archive is broken"
echo "ok ($(tar -tzf "$w/files.tgz" | grep -vc '/$') files)"

echo "== 4/6 row counts"
$dc exec -T db psql -U "$PGU" -d "$PGD" -At -c "SELECT format('SELECT %L || ''='' || count(*) FROM %I.%I;', table_schema||'.'||table_name, table_schema, table_name) FROM information_schema.tables WHERE table_type='BASE TABLE' AND (table_schema LIKE 'workspace_%' OR table_schema='core') ORDER BY 1" \
  | $dc exec -T db psql -U "$PGU" -d "$PGD" -At | tr -d '\r' > "$w/row-counts.txt"
echo "ok ($(wc -l < "$w/row-counts.txt" | tr -d ' ') tables). Main ones:"
grep -E '\.(person|company|_ticket|_serviceRequest|_interaction|_catalogEntry|note|workflow|workspaceMember)=' "$w/row-counts.txt" | sed 's/^workspace_[a-z0-9]*\./  /' || true

echo "== 5/6 secrets (values are NOT shown)"
: > "$w/secrets.env"; chmod 600 "$w/secrets.env"
for k in APP_SECRET ENCRYPTION_KEY FALLBACK_ENCRYPTION_KEY TAG SERVER_URL PG_DATABASE_USER PG_DATABASE_NAME; do
  v=$(getenv "$k"); printf '%s=%s\n' "$k" "$v" >> "$w/secrets.env"
  if [ -n "$v" ]; then echo "  $k: present"; else echo "  $k: empty"; fi
done
[ -n "$(getenv ENCRYPTION_KEY)" ] || fail "ENCRYPTION_KEY is empty in .env: stop and tell Rishi"

echo "== 6/6 encrypt"
read -r -s -p "Choose a passphrase (min 12 characters): " p1; echo
read -r -s -p "Type it again: " p2; echo
[ "$p1" = "$p2" ] || fail "the two passphrases differ"
[ ${#p1} -ge 12 ] || fail "passphrase shorter than 12 characters"
out="$HOME/Desktop/twenty-export-$stamp.enc"
tar -C "$w" -czf - . | PASSX="$p1" openssl enc -aes-256-cbc -pbkdf2 -iter 600000 -salt -pass env:PASSX -out "$out"
PASSX="$p1" openssl enc -d -aes-256-cbc -pbkdf2 -iter 600000 -pass env:PASSX -in "$out" | tar -tzf - | grep -q 'twenty-db.sql.gz' || fail "self-check: the file does not open again"
unset p1 p2
echo
echo "DONE: $out ($(du -h "$out" | cut -f1))"
echo "sha256: $(shasum -a 256 "$out" | cut -d' ' -f1)"
echo
echo "Next:"
echo "  1. Send that file to Rishi (Teams or Google Drive)."
echo "  2. Tell Rishi the passphrase by phone or WhatsApp, NOT in the same chat as the file."
echo "  3. From now on, changes made in this laptop CRM will NOT be in the cloud copy."
echo "  4. Keep this laptop CRM as it is until Rishi confirms the cloud is live (it is the fallback)."
