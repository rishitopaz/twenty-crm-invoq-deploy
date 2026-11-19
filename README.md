# Twenty CRM for INVOQ: Cloud Deployment

This repository puts **Aroosh Ahmed's Twenty CRM** (Retail tickets + the generic Service Request module for INVOQ)
on a cloud server with a real web address, and lets anyone at Topaz deploy the same CRM on their own server.

- **Built by (the CRM):** Aroosh Ahmed. She designs and configures the CRM.
- **Deployed by (this repo):** Rishi Upadhyay. He puts it on servers and keeps it running.
- **For:** Umaima Suleman (team lead).
- **Last updated:** 19 November 2026.

---

## 1. The links

| What | Link | Who uses it |
|---|---|---|
| **The live CRM** | https://crm.34-18-187-167.sslip.io | Everyone, every day. This is the normal login page |
| **This repository** | https://github.com/rishitopaz/twenty-crm-invoq-deploy | Anyone who wants to deploy it on another server |
| **Aroosh's design repo** | https://github.com/aroosh77/twenty-crm-invoq | Her original files and documents (copies are in `docs/aroosh/`) |

New people join with an **invite link** that an Admin creates in the CRM (Settings → Members). Public sign-up is
switched off, so strangers cannot make accounts. After joining, everyone uses the normal link above.

---

## 2. Where things stand today

| Part | Status |
|---|---|
| CRM running on Google Cloud with HTTPS (padlock in the browser) | **Done** |
| Data model: Tickets, Service Requests, Interactions, Catalog Entries, retail fields on People | **Done**, rebuilt from Aroosh's documents |
| Sample records (tickets, service requests, interactions, the 20 catalog entries) | **Done**, rebuilt from her documents |
| Roles: Admin, Member, Agent, Supervisor | **Done** |
| Umaima's login | **Done** (Supervisor) |
| Aroosh's **exact** laptop data (every record, her original users and API keys) | **Waiting** for Aroosh to run one export script (about 5 minutes) |
| Email automations (High-priority alert, SLA breach alert) | **Not yet**. They need a mailbox connected in the CRM |
| Automatic backups of the cloud server | **Not yet**. Planned next |

Full detail of what is live and what is missing: [docs/LIVE-CLOUD-COPY.md](docs/LIVE-CLOUD-COPY.md).

---

## 3. How it works (one picture)

```
   Your browser / Postman / INVOQ
                |
                |  https://crm.34-18-187-167.sslip.io   (encrypted, certificate renews itself)
                v
   +---------------- Google Cloud server "aroosh-crm" (Doha region) ----------------+
   |                                                                               |
   |   Caddy  ----->  Twenty server  ----->  PostgreSQL database (all the records) |
   |   (HTTPS)        (web app + API)  \                                           |
   |                                    ->  Redis (queues)                         |
   |                  Twenty worker  ------^  (background jobs, workflows)         |
   +-------------------------------------------------------------------------------+
```

Five small programs ("containers") run together, started with one command. Only Caddy faces the internet, on
ports 80 and 443. The database is never reachable from outside.

**About the address:** `sslip.io` is a free service that turns the server's IP address (34.18.187.167) into a web
name, so we get a real HTTPS certificate without buying a domain. A company domain (for example
`crm.topaz.ae`) can replace it at any time: see [docs/OPERATIONS.md](docs/OPERATIONS.md), "Use your own domain".

---

## 4. What is in this repository

| File | What it is, in plain words |
|---|---|
| `README.md` | This page |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | **How to deploy the CRM on a new server**, step by step |
| [`docs/LIVE-CLOUD-COPY.md`](docs/LIVE-CLOUD-COPY.md) | What exactly is on the live cloud CRM, what was rebuilt, what is missing |
| [`docs/OPERATIONS.md`](docs/OPERATIONS.md) | Day-to-day: add people, start/stop, backups, upgrades, own domain, costs, fixing problems |
| `docs/aroosh/` | Aroosh's own documents: the project history and the API guide (how to call the CRM from other software) |
| `docker-compose.yml` | The list of the five programs and how they connect |
| `Caddyfile` | The HTTPS settings |
| `.env.example` | The settings template (the real `.env` holds passwords and is never put in GitHub) |
| `scripts/setup-ubuntu.sh` | Prepares an empty Ubuntu server: Docker, firewall, security updates |
| `scripts/import-export.sh` | Deploys the CRM **with Aroosh's exact data** from an export file |
| `scripts/build_from_docs.py` | Builds the CRM structure and sample records **from Aroosh's documents** (used for today's live copy) |
| `scripts/export-from-laptop.sh` | What Aroosh runs on her Mac to make the export file |
| `data/` | Where the encrypted export file goes (empty until Aroosh sends it) |

---

## 5. Common questions

**Is there a size limit?** Not in practice. The server has a 40 GB disk with 30 GB free; today's CRM data uses
27 MB. Hundreds of thousands of records fit. The disk can be enlarged in minutes if ever needed.

**What does it cost?** About **USD 30 to 35 per month** for this server on Google Cloud (2 processors, 4 GB memory,
40 GB disk, fixed IP address). It currently runs on the Google Cloud trial credit. Check the trial's end date in
the Google Cloud billing page: when a trial ends, servers stop unless billing is switched to a paid account.

**Can we run it on our own (internal) server instead?** Yes, that is what [DEPLOYMENT.md](DEPLOYMENT.md) is for.
Any Ubuntu server with 2 processors, 4 GB memory and 30 GB disk works. Internet access is needed to download the
programs; HTTPS needs a name that points to the server.

**Can INVOQ or other software use it?** Yes, through the REST API: `https://crm.34-18-187-167.sslip.io/rest/...`
with an API key (Settings → APIs & Webhooks). Every example in `docs/aroosh/twenty-crm-retail-api.md` works; only
replace `http://localhost:3000` with the live address.

**Can it be shown inside INVOQ (screen pop / iframe)?** Yes. An Admin adds INVOQ's address under
Settings → General → Security → Iframe embedding.

**Is the data safe?** The connection is encrypted (HTTPS), the database is not reachable from the internet, the
server firewall only allows web traffic and administrator SSH, and nobody can sign up without an invitation.
Automatic backups are the next step (see section 2).

**Who do I ask?** Rishi for the server and deployment, Aroosh for how the CRM itself is configured.
