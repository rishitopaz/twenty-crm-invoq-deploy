# The live cloud CRM: what is on it

**Address:** https://crm.34-18-187-167.sslip.io
**State on:** 19 November 2026, 12:20 UTC

The live CRM is an **exact copy of Aroosh's laptop CRM** as she exported it on 19 November 2026 at 10:14 UTC:
every record, her users and passwords, roles, workflows, API keys and the connected mailbox.

---

## 1. The server

| Item | Value |
|---|---|
| Provider | Google Cloud, region me-central1 (Doha), zone me-central1-a |
| Server name | `aroosh-crm` |
| Size | e2-medium: 2 processors, 4 GB memory (+2 GB swap), 40 GB disk (29 GB free) |
| Operating system | Ubuntu 24.04.5 LTS, automatic security updates on |
| Fixed IP address | 34.18.187.167 (reserved as `aroosh-crm-ip`, so it never changes) |
| Firewall | Google Cloud: only ports 80 and 443 from the internet, SSH only through Google's secure tunnel (IAP). Server firewall (ufw): SSH, 80, 443 |
| Twenty version | **v2.51.0**, the same version and the same build as Aroosh's laptop (pinned; it changes only when someone upgrades on purpose) |
| Other programs | PostgreSQL 16 (database), Redis 7 (queues), Caddy 2 (HTTPS) |
| HTTPS certificate | Let's Encrypt, issued and renewed automatically by Caddy |
| Database size | 26 MB |
| Public sign-up | **Off**: people join only with an invite link (Invite by link is currently off too) |
| Separate from | Rishi's own Real Estate CRM (`twenty-crm`, another server). The two share nothing |

## 2. How the content got there

1. Aroosh ran `scripts/export-from-laptop.sh` on her Mac. It made one encrypted file,
   `twenty-export-20261119-1414.enc` (36 MB), with her database, uploaded files, settings and version.
2. On the server, `scripts/import-export.sh` opened the file and loaded it ([DEPLOYMENT.md](../DEPLOYMENT.md), Way A).
3. The check at the end compared all 45 data tables with the counts taken on her laptop: **DATA IDENTICAL**.
4. A second, separate check counted the records one type at a time (table below): all match.

Before this, the live copy had been rebuilt from her documents (Way B). That version was replaced. It is kept
as a backup on the server and as a Google Cloud disk snapshot (see [OPERATIONS.md](OPERATIONS.md)).

## 3. Records (checked on the live CRM after the import)

| Type | On Aroosh's laptop | On the cloud |
|---|---|---|
| Tickets | 18 | 18 |
| Service Requests | 12 | 12 |
| People | 14 | 14 |
| Companies | 3 (Urban Wear Boutique, Simra's Bookstore, Notion) | 3 |
| Catalog Entries | 20 | 20 |
| Interactions | 12 | 12 |
| Notes | 9 | 9 |
| Workflows | 6 | 6 |
| API keys | 3 (2 active) | 3 (2 active) |
| Users | 3 | 3 |

## 4. People and roles

| Person | Role | How they log in |
|---|---|---|
| Aroosh Ahmed | Admin | Her usual email and password from her laptop CRM |
| Umaima Suleman | Supervisor | The email and password she used on Aroosh's laptop CRM (not a password made on the earlier cloud copy) |
| Test Agent | Agent | Aroosh's test account |

Roles in the workspace: Admin, Member, Agent, Supervisor, API Integration, External API access (plus Twenty's
system role "Workspace Custom Application": leave it alone).

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
other, and only the copy where it was created sends its alert. From now on, use the cloud address for real work.

## 6. API keys

| Key | Expires |
|---|---|
| Retail CRM | 4 October 2126 |
| Umaima external | **21 November 2026**: create a new key before then if it is still used (Settings → APIs & Webhooks) |

Keys made on her laptop work unchanged on the cloud: same keys, only the address changes from
`http://localhost:3000` to `https://crm.34-18-187-167.sslip.io`.

## 7. Not done yet

| Item | Note |
|---|---|
| Automatic backups | Manual backups and snapshots only, so far ([OPERATIONS.md](OPERATIONS.md), "Backups") |
| Server email (password reset, invitations by email) | Invite by link works without it |
| Two-step login (2FA) | 0 users use it |
| Iframe embedding for INVOQ | Waiting for INVOQ's agent-screen address (Settings → General → Security → Iframe embedding) |
