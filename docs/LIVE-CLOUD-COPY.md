# The live cloud CRM: what is on it

**Address:** https://crm.34-18-187-167.sslip.io
**State on:** 26 November 2026, 09:10 UTC

The live CRM is an **exact copy of Aroosh's laptop CRM** as she exported it on **26 November 2026 at 08:31 UTC**
(file `twenty-export-20261126-1231.enc`), then upgraded to v2.59.3: every record, her users and passwords, roles,
workflows, API keys and the connected mailbox.

---

## 1. The server

| Item | Value |
|---|---|
| Provider | Google Cloud, region me-central1 (Doha), zone me-central1-a |
| Server name | `aroosh-crm` |
| Size | e2-medium: 2 processors, 4 GB memory (+2 GB swap), 40 GB disk (25 GB free on 26 Nov 2026) |
| Operating system | Ubuntu 24.04.5 LTS, automatic security updates on |
| Fixed IP address | 34.18.187.167 (reserved as `aroosh-crm-ip`, so it never changes) |
| Firewall | Google Cloud: only ports 80 and 443 from the internet, SSH only through Google's secure tunnel (IAP). Server firewall (ufw): SSH, 80, 443 |
| Twenty version | **v2.59.3** since 26 Nov 2026 (upgraded from v2.51.0, Aroosh's laptop version, at her request; pinned, it changes only when someone upgrades on purpose). Upgraded twice on 26 Nov (before and after loading Aroosh's newer data). Undo points: snapshots `pre-upgrade-aroosh-v2-59-3-20261126-0611` and `pre-reload-aroosh-20261126-0838`, backups in `~/backups/` |
| Other programs | PostgreSQL 16 (database), Redis 7 (queues), Caddy 2 (HTTPS) |
| HTTPS certificate | Let's Encrypt, issued and renewed automatically by Caddy |
| Database size | 31 MB (26 Nov 2026) |
| Public sign-up | **Off**: people join only with an invite link (Invite by link is currently off too) |
| Separate from | Rishi's own Real Estate CRM (`twenty-crm`, another server). The two share nothing |

## 2. How the content got there

1. **19 Nov 2026:** Aroosh's first export (`twenty-export-20261119-1414.enc`) was loaded with `scripts/import-export.sh`
   ([DEPLOYMENT.md](../DEPLOYMENT.md), Way A). Check: **DATA IDENTICAL** (all 45 data tables).
2. **26 Nov 2026, 06:12 UTC:** upgraded v2.51.0 → v2.59.3 at Aroosh's request ([OPERATIONS.md](OPERATIONS.md), section 4).
3. **26 Nov 2026, 08:44 UTC:** Aroosh's **newer export** (made 08:31 UTC on her laptop) was loaded the same way.
   Check: **DATA IDENTICAL** (all 45 data tables). This **replaced** the cloud data. What only the cloud had is not in
   the live CRM any more: one ticket Aroosh created on the cloud on 20 Nov, Rishi's Member login, and emails synced
   after 19 Nov. All of it is kept in the backup `~/backups/crm-20261126-0838.sql.gz` and the snapshot
   `pre-reload-aroosh-20261126-0838`.
4. **26 Nov 2026, 08:52 UTC:** upgraded again to v2.59.3 (healthy at 08:57). The automations ran at 09:00 and completed;
   no ticket or service request was past its deadline, so no duplicate alert emails.
5. **26 Nov 2026, 09:07 UTC:** an encrypted copy of the live data was saved in this repository:
   `data/twenty-export-20261126-1305.enc` (about 73 MB, Twenty v2.59.3, so Way A loads it at the current version).
   Only Rishi has its passphrase (by phone). **Restore-tested on 26 Nov 2026:** it opened with the passphrase and its
   database loaded into a scratch PostgreSQL with all 125 tables row-for-row identical, 0 load errors. The older copy (20 Nov) was removed from the current files; it stays in git history.

## 3. Records (live, not deleted, 26 Nov 2026)

| Type | First copy (19 Nov) | Now (26 Nov) |
|---|---|---|
| Tickets | 18 | 18 |
| Service Requests | 12 | **25** (13 new: 2 on 20 Nov, 4 on 24 Nov, 6 on 25 Nov, 1 on 26 Nov) |
| People | 14 | **19** |
| Companies | 3 | 3 |
| Catalog Entries | 20 | 21 |
| Interactions | 12 | 12 |
| Notes | 9 | 9 |
| Workflows | 6 | 6 |
| API keys (active) | 2 | 2 |
| Users (people who can log in) | 3 | 3 |

The database also keeps records that were **deleted** in the CRM (Service Requests 31 in total, People 22, Companies 7,
Catalog Entries 22). Only the live numbers above are what people see.

**Do not reload an older export over the live CRM:** it would erase everything made since that export.

## 4. People and roles

| Person | Role | How they log in |
|---|---|---|
| Aroosh Ahmed | Admin | Her usual email and password from her laptop CRM |
| Umaima Suleman | Supervisor | The email and password she uses on Aroosh's laptop CRM |
| Test Agent | Agent | Aroosh's test account |

Rishi is **not** a member since the 26 Nov reload (his login was only on the cloud). Aroosh re-invites him if needed.
Only an Admin (today: Aroosh) can change roles, settings or create API keys.

Roles in the workspace: Admin, Member, Agent, Supervisor, API Integration, External API access (plus Twenty's
system roles "Workspace Custom Application" and "Standard role": leave them alone).

**Forgotten password:** "Forgot password" needs the server to send email, which is not set up. Aroosh (Admin)
removes and re-invites the person instead.

## 5. Automations (workflows)

| Workflow | When it runs | What it does |
|---|---|---|
| SLA breach escalation | Every 15 minutes | Finds open tickets past their resolution deadline that are still On Track or At Risk, marks them Breached, emails one alert each |
| SLA breach escalation (service requests) | Every 15 minutes | The same for service requests |
| High priority ticket email | When a ticket is created with High or Urgent priority | Emails an alert |
| High priority service request email | When a service request is created with High or Urgent priority | Emails an alert |
| Create company when adding a new person | When a person is created | Twenty's built-in automation |
| Quick Lead | By hand | Twenty's built-in automation |

The alert emails go out through her connected mailbox (IMAP/SMTP), which works on the cloud too. First cloud run
at 12:15 UTC: completed, nothing to alert about (the only open records past their deadline, TKT-0020 and SR-0004,
were already Breached), 0 emails sent.

**Two copies for now:** Aroosh's laptop CRM still exists. A ticket created on one copy does not appear on the
other, and only the copy where it was created sends its alert. Since 26 Nov the cloud holds Aroosh's latest data:
use the cloud address for real work.

## 6. API keys

| Key | Expires |
|---|---|
| Retail CRM | 4 October 2126 |
| Umaima external | **4 December 2026** (renewed on Aroosh's laptop; came with the 26 Nov data). Aroosh creates a new one when needed |

Keys made on her laptop came over with her data (same keys; only the address changes from `http://localhost:3000` to
`https://crm.34-18-187-167.sslip.io`). They were not re-tested after the 26 Nov 2026 upgrade. Only an Admin can
create new keys.

## 7. Not done yet

| Item | Note |
|---|---|
| Backup copy **off** the server (Google Drive) | The nightly backup and the daily disk snapshot exist since 25 Nov 2026 ([OPERATIONS.md](OPERATIONS.md), "Backups"); a Drive copy is still to do |
| Server email (password reset, invitations by email) | Invite by link works without it |
| Two-step login (2FA) | No user has it switched on |
| Iframe embedding for INVOQ | Waiting for INVOQ's agent-screen address (Settings → General → Security → Iframe embedding) |
