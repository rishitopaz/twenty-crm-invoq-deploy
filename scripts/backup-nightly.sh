#!/usr/bin/env bash
# scripts/backup-nightly.sh   nightly backup of the CRM database and uploaded files, kept on the server for 7 days.
# Run on the server from cron (see docs/OPERATIONS.md, section 3). Safe to run by hand any time: it only READS the CRM.
#   scripts/backup-nightly.sh
# Writes ~/backups/crm-<UTC date-time>.sql.gz and ~/backups/files-<UTC date-time>.tgz (private, mode 600), checks both are
# readable and complete, then deletes backups older than KEEP_DAYS (default 7). A broken backup is never kept and never
# replaces a good one: on any problem the script prints "BACKUP FAILED: <why>" and exits 1 (cron writes it to ~/backup.log).
# After a good run it writes ~/backups/LAST-OK (the time), so "is the backup alive?" is one command: cat ~/backups/LAST-OK
# This is a copy ON THE SAME SERVER: it protects against mistakes and bad upgrades. Against losing the whole server, the daily
# Google Cloud disk snapshot is the second copy, and copying a backup off the server is the third (OPERATIONS.md).
set -euo pipefail
umask 077
cd "$(dirname "$0")/.."
[ -f .env ] || { echo "BACKUP FAILED: no .env here (run from the repository folder on the server)"; exit 1; }
dir="${BACKUP_DIR:-$HOME/backups}"; keep="${KEEP_DAYS:-7}"
mkdir -p "$dir"; chmod 700 "$dir"
dc="sudo -n docker compose --env-file .env"
stamp=$(date -u +%Y%m%d-%H%M)
tmpd=$(mktemp -d "$dir/.tmp.XXXXXX"); trap 'rm -rf "$tmpd"' EXIT
fail() { echo "$(date -u +%FT%TZ) BACKUP FAILED: $*"; exit 1; }

$dc exec -T db pg_dump -U postgres default </dev/null | gzip > "$tmpd/crm.sql.gz" || fail "database dump"
gzip -t "$tmpd/crm.sql.gz" || fail "database dump archive is broken"
gzip -dc "$tmpd/crm.sql.gz" | tail -c 300 | grep -q 'PostgreSQL database dump complete' || fail "database dump is incomplete"
$dc exec -T server tar -C /app/packages/twenty-server -czf - .local-storage </dev/null > "$tmpd/files.tgz" || fail "files archive"
tar -tzf "$tmpd/files.tgz" >/dev/null || fail "files archive is broken"

mv "$tmpd/crm.sql.gz" "$dir/crm-$stamp.sql.gz"; mv "$tmpd/files.tgz" "$dir/files-$stamp.tgz"
date -u +%FT%TZ > "$dir/LAST-OK"
find "$dir" -maxdepth 1 -type f \( -name 'crm-*.sql.gz' -o -name 'files-*.tgz' \) -mtime +"$keep" -delete
echo "$(date -u +%FT%TZ) backup ok: crm-$stamp.sql.gz ($(du -h "$dir/crm-$stamp.sql.gz" | cut -f1)), files-$stamp.tgz ($(du -h "$dir/files-$stamp.tgz" | cut -f1)); $(ls "$dir"/crm-*.sql.gz | wc -l) kept"
