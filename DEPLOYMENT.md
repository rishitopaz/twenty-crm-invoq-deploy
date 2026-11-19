# Twenty CRM (INVOQ / Retail): Deployment Guide

This repository deploys Aroosh Ahmed's Twenty CRM (workspace **Topaztel**: Retail Tickets, Service Requests,
Interactions, Category Catalog, workflows, roles and users) on any Linux server, **with the exact data** as exported
from her laptop.

| What | Where |
|---|---|
| Containers | `docker-compose.yml`: Twenty server, Twenty worker, PostgreSQL 16, Redis 7, Caddy (automatic HTTPS) |
| Data | `data/twenty-export-<date>.enc`: database dump + uploaded files + secrets + version + row counts, AES-256 encrypted. The passphrase is shared separately, never in this repo |
| Scripts | `scripts/setup-ubuntu.sh` (prepare server), `scripts/import-export.sh` (deploy the data), `scripts/export-from-laptop.sh` (make a new export), `scripts/build_from_docs.py` (rebuild the data model and sample records from Aroosh's docs on an empty workspace, if no export is available) |

> **Status (19 Nov 2026):** live copy being set up on Google Cloud at `https://crm.34-18-187-167.sslip.io`.
> The encrypted export of Aroosh's laptop data will be added to `data/` as soon as it is made; until then the
> cloud copy is rebuilt from her documentation with `scripts/build_from_docs.py`.
| Design and API | Aroosh's docs: `twenty-crm-project-history.md`, `twenty-crm-retail-api.md` (repo `aroosh77/twenty-crm-invoq`) |

---

## 1. What you need

- A Linux server: **Ubuntu 24.04 or 22.04**, at least **2 vCPU, 4 GB RAM, 30 GB disk** (tested on Google Cloud e2-medium).
- Ports **80 and 443** open to the internet (for HTTPS), and SSH for yourself.
- The **passphrase** of the export file (ask Rishi or Aroosh; it is never written in the repo).
- Optional: a domain name. Without one, the guide uses `sslip.io`, which turns the server IP into a hostname
  (`crm.203-0-113-10.sslip.io`) and gets a real HTTPS certificate automatically.

## 2. Prepare the server (once, about 2 minutes)

```bash
git clone https://github.com/<owner>/twenty-crm-invoq-deploy.git
cd twenty-crm-invoq-deploy
sudo bash scripts/setup-ubuntu.sh
```

This installs Docker from Docker's official repository, turns on the firewall (SSH, 80, 443 only), automatic security
updates, and a swap file on small machines. Log out and back in once so your user can run `docker`.

## 3. Deploy with the data (about 5 to 10 minutes)

```bash
cd twenty-crm-invoq-deploy
scripts/import-export.sh data/twenty-export-<date>.enc
```

It asks for the passphrase, then by itself:
1. opens the export and writes `.env` with the **same APP_SECRET and ENCRYPTION_KEY** as the original CRM (so existing
   logins, API keys and the connected mailbox keep working), the **same Twenty version**, and a new random database password;
2. starts PostgreSQL and loads the database;
3. starts Twenty and Caddy, and restores the uploaded files;
4. compares the row count of every table with the original and prints `DATA IDENTICAL` when they match.

With your own domain, point an A record at the server first and pass it:
`scripts/import-export.sh data/twenty-export-<date>.enc crm.yourcompany.com`

The last lines print the address, for example `LIVE: https://crm.203-0-113-10.sslip.io`.

## 4. Check it works

1. Open the address. Log in with the **same email and password** as on the original CRM.
2. Tickets, Service Requests, Interactions and Catalog Entries should be in the left menu with all records.
3. API: the same keys work; only the base URL changes from `http://localhost:3000` to `https://<host>`:
   ```bash
   curl -s -H "Authorization: Bearer <API_KEY>" "https://<host>/rest/serviceRequests?limit=1"
   ```
   No key gives `403 Missing authentication token` (this also proves the address reaches Twenty).
4. Settings → Workflows: the priority alert and SLA breach workflows are there and active.

## 5. Day-to-day commands (from the repo folder)

| Task | Command |
|---|---|
| Status | `docker compose --env-file .env ps` |
| Logs | `docker compose --env-file .env logs server --tail 50` |
| Stop / start | `docker compose --env-file .env stop` / `docker compose --env-file .env up -d` |
| Database backup | `docker compose --env-file .env exec -T db pg_dump -U postgres default \| gzip > backup-$(date +%F).sql.gz` |

Never run `docker compose down -v`: `-v` deletes the database volume.

## 6. Important notes

- **One live copy.** After the cloud copy is live, the original laptop CRM should be stopped. Otherwise both run the
  SLA workflow every 15 minutes and send duplicate emails, and changes made in one do not appear in the other.
- **Same version first.** The data must start on the Twenty version it came from (`TAG` in `.env`). Upgrade later by
  changing `TAG` and running `docker compose --env-file .env up -d` after a backup.
- **Secrets.** `.env` holds the secrets; it is never committed (`.gitignore`). Anyone with the export file **and** the
  passphrase can read all CRM data and log in as its users, so share the passphrase only privately.
- **Iframe screen pop.** Add the INVOQ agent-screen address under Settings → General → Security → Iframe embedding.
- **Sign-up** from the public internet is disabled (`IS_SIGN_UP_DISABLED`); members join by invitation.

## 7. Making a fresh export (if the original CRM changed)

On the machine where the original runs (Mac with Docker Desktop), from its Twenty folder:

```bash
bash scripts/export-from-laptop.sh ~/twenty
```

It only reads, never changes the CRM, and writes one encrypted file to the Desktop. Put it in `data/` and deploy as in step 3.

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| `wrong passphrase or damaged file` | Retype the passphrase; check the file size matches the one in the repo |
| Server not healthy | `docker compose --env-file .env logs server --tail 50`; a first start can take 2 to 3 minutes |
| Browser shows a certificate error | Wait one minute after the first start; ports 80 and 443 must be open |
| Login works but the API key is refused | `APP_SECRET` differs from the original; it must come from the export |
| Mailbox shows an error | `ENCRYPTION_KEY` differs from the original, or the mailbox password was changed; reconnect it under Settings → Accounts |
| `.env already exists` | The server was already set up; for a failed first try: `FORCE=1 scripts/import-export.sh ...` |
