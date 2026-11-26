# Running the CRM day to day

Commands are run **on the server**, inside the repository folder (`cd ~/twenty-crm-invoq-deploy`).
For the live copy, the server is reached from a computer with the Google Cloud CLI:

```bash
gcloud compute ssh aroosh-crm --zone=me-central1-a --tunnel-through-iap
```

---

## 1. People and access (in the CRM screen, no commands)

| Task | Where |
|---|---|
| Invite someone | Settings → Members → **Invite by link** → copy the link, send it privately. Switch it off once they have joined (anyone with the link can join) |
| Change someone's role | Settings → Members → the person → **Permissions** → Role → Update role |
| Remove someone | Settings → Members → the person → Remove |
| Roles | **Admin**: everything incl. settings. **Supervisor**: see, edit and delete records. **Agent**: see and edit, no delete. **Member**: Twenty's default |
| API key for another system (INVOQ, Postman) | Settings → **APIs & Webhooks** → Create API key. Choose the role carefully (not Admin for outside systems), set an expiry, copy it once, send it privately |
| Revoke an API key | Settings → APIs & Webhooks → the key → Delete. It stops working at once |
| Allow embedding in INVOQ (screen pop) | Settings → General → Security → **Iframe embedding** → add INVOQ's address (for example `https://agent.invoq.example`) |

## 2. Start, stop, status, logs

| Task | Command |
|---|---|
| Status of the five programs | `docker compose --env-file .env ps` |
| Start (or apply a settings change) | `docker compose --env-file .env up -d` |
| Stop (data is kept) | `docker compose --env-file .env stop` |
| Restart only the CRM | `docker compose --env-file .env restart server worker` |
| Last log lines of the CRM | `docker compose --env-file .env logs server --tail 50` |
| Is the site up? (from anywhere) | `curl -s -o /dev/null -w '%{http_code}\n' https://crm.34-18-187-167.sslip.io/healthz` → `200` |

**Never run `docker compose down -v`.** The `-v` deletes the database. `stop` or plain `down` are safe.

The programs restart by themselves after a crash or a server reboot (`restart: always`).

## 3. Backups

**Automatic, since 25 November 2026:**
- **Every night at 03:30 UTC** `scripts/backup-nightly.sh` saves the database and the uploaded files into `~/backups/` on
  the server (files `crm-<date>.sql.gz` and `files-<date>.tgz`, private, last 7 days kept). It checks each file is complete
  before keeping it and never replaces a good backup with a broken one. A failure prints `BACKUP FAILED` in `~/backup.log`.
  Is it alive? `cat ~/backups/LAST-OK` shows the time of the last good backup (a date older than 1 day means it stopped).
- **Every day at 23:00 UTC** Google Cloud takes a snapshot of the whole server disk and keeps 7
  (schedule `aroosh-daily`; list them: `gcloud compute snapshots list --filter="sourceDisk~aroosh-crm"`). Cost: well under
  USD 1 a month.
- Tested on 25 November 2026: a backup was made by hand, loaded into a scratch database and gave the same users and tickets
  as the live CRM (4 users, 19 tickets). Not tested: restoring a whole disk from one of these snapshots on this server.
- Not done: a copy of the backups **off** the server (Google Drive). The snapshots are the second copy for now.

**Make one by hand** before any change (the nightly script does the same: run `scripts/backup-nightly.sh`):

```bash
mkdir -p backups
docker compose --env-file .env exec -T db pg_dump -U postgres default | gzip > backups/crm-$(date +%F-%H%M).sql.gz
docker compose --env-file .env exec -T server tar -C /app/packages/twenty-server -czf - .local-storage > backups/files-$(date +%F-%H%M).tgz
```

The first file is the whole database, the second the uploaded files. Copy them off the server
(`gcloud compute scp aroosh-crm:~/twenty-crm-invoq-deploy/backups/<file> . --zone=me-central1-a --tunnel-through-iap`).
A backup also needs `.env` (same `APP_SECRET` and `ENCRYPTION_KEY`) to be useful: keep a copy of `.env` in a
password manager.

**Undo points kept from the 19 Nov 2026 switch to Aroosh's exact data:** the Google Cloud snapshot
`pre-plana-aroosh-20261119-1205` and the backup folder `~/pre-import-20261119-1203` on the server (the earlier
rebuilt copy). They can be deleted once everyone is happy with the live copy.

**Planned:** copy the nightly backup, encrypted, to Google Drive as well (already running for Rishi's other CRM).

**Restore a backup** (replaces everything that is in the CRM now):

```bash
docker compose --env-file .env stop server worker caddy
docker compose --env-file .env exec -T db psql -U postgres -d postgres -c 'DROP DATABASE "default" WITH (FORCE)' -c 'CREATE DATABASE "default"'
gzip -dc backups/crm-<date>.sql.gz | docker compose --env-file .env exec -T db psql -U postgres -d default -q -o /dev/null
docker compose --env-file .env up -d
docker compose --env-file .env exec -T server tar -C /app/packages/twenty-server -xzf - < backups/files-<date>.tgz
```

## 4. Upgrading Twenty to a newer version

1. Make a backup (section 3).
2. Read Twenty's release notes for the new version (https://github.com/twentyhq/twenty/releases).
3. In `.env`, change `TAG=v2.51.0` (today's version, same as Aroosh's laptop) to the new one, for example `TAG=v2.59.2`.
4. `docker compose --env-file .env pull && docker compose --env-file .env up -d`
5. Wait until `server` is **(healthy)** (database upgrades can take a few minutes), then log in and check.

To go back: set the old `TAG` again **and** restore the backup from step 1 (the database upgrade does not undo
itself).

## 5. Use your own domain instead of sslip.io

1. In your DNS, create an A record, for example `crm.topaz.ae` → `34.18.187.167`.
2. In `.env`, set `CRM_HOST=crm.topaz.ae`.
3. `docker compose --env-file .env up -d`. Caddy gets a certificate for the new name within a minute.
4. Tell users the new address; update any API integrations (base URL) and the iframe setting.

## 6. Internal servers without internet access

The automatic certificate (Let's Encrypt) needs the server to be reachable from the internet on port 80.
On an internal-only server, either:
- use a certificate from your company's IT: put the two files on the server and add the line
  `tls /path/cert.pem /path/key.pem` inside the `{$CRM_HOST} { ... }` block of `Caddyfile`; or
- for testing only, add `tls internal` inside the block (browsers will show a warning until the internal
  certificate is trusted).

The server still needs to download the programs once (Docker Hub). Without that, IT can copy the images in with
`docker save` / `docker load`.

## 7. Disk, memory and cost

| Check | Command | Healthy |
|---|---|---|
| Free disk | `df -h /` | More than 5 GB free |
| Memory | `free -h` | Some "available" memory left |
| Database size | `docker compose --env-file .env exec -T db psql -U postgres -d default -Atc "select pg_size_pretty(pg_database_size('default'))"` | (27 MB on 19 Nov 2026) |

Bigger disk on Google Cloud: `gcloud compute disks resize aroosh-crm --size=80GB --zone=me-central1-a`
(Ubuntu grows the partition by itself after a reboot).

**Cost** of the live server on Google Cloud: about USD 30 to 35 per month (e2-medium server, 40 GB disk, fixed IP).
It runs on the Google Cloud trial credit today. Check the trial's end date in the billing page: when a trial ends,
servers stop unless billing is upgraded to a paid account.

## 8. Fixing common problems

| Problem | Likely cause | Fix |
|---|---|---|
| Site does not open | Server or programs stopped | `docker compose --env-file .env ps`; if not running: `up -d`. Check the server is running in the Google Cloud console |
| "Bad gateway" (502) | The CRM is still starting | Wait 2 minutes; `logs server --tail 50` |
| Certificate warning | New name, or ports 80/443 closed | Wait a minute; check the firewall rule `twenty-web` and `CRM_HOST` |
| Cannot sign up | Public sign-up is off on purpose | Ask an Admin for an invite link |
| Someone forgot their password | | "Forgot password" on the login page needs email sending, which is not set up yet: an Admin removes and re-invites them |
| API returns 403 "Missing authentication token" | No key sent | Add the header `Authorization: Bearer <API_KEY>` |
| API returns 400 "PERMISSION_DENIED" | The key's role does not allow that | Use a key with a role that allows it, or change the role's rules |
| Workflows do not send email | No mailbox connected | Settings → Accounts → connect a mailbox with send permission |
| Disk full | Logs or backups | Delete old files in `backups/`; logs are already capped at 50 MB per program |

## 9. Security rules

- Never put passwords, API keys, the `.env` file or the export passphrase in GitHub, chat, email or documents.
- Keep public sign-up off (`IS_SIGN_UP_DISABLED=true` in `.env`); switch Invite by link off when not inviting.
- Give outside systems their own API key with the narrowest role and an expiry; delete keys nobody uses.
- Only trusted Admins may edit workflows: workflow code steps run on the server.
