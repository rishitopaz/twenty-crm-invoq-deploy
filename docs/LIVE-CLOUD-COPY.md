# The live cloud CRM: what is on it

**Address:** https://crm.34-18-187-167.sslip.io
**State on:** 19 November 2026

This page says exactly what is on the live CRM, where each part came from, and what is still missing.
It is honest about guesses: where Aroosh's documents did not give a value, the value used is marked **(assumed)**.

---

## 1. The server

| Item | Value |
|---|---|
| Provider | Google Cloud, region me-central1 (Doha), zone me-central1-a |
| Server name | `aroosh-crm` |
| Size | e2-medium: 2 processors, 4 GB memory (+2 GB swap), 40 GB disk (30 GB free) |
| Operating system | Ubuntu 24.04.5 LTS, automatic security updates on |
| Fixed IP address | 34.18.187.167 (reserved as `aroosh-crm-ip`, so it never changes) |
| Firewall | Google Cloud: only ports 80 and 443 from the internet, SSH only through Google's secure tunnel (IAP). Server firewall (ufw): SSH, 80, 443 |
| Twenty version | **v2.59.2** (pinned; it changes only when someone upgrades on purpose) |
| Other programs | PostgreSQL 16 (database), Redis 7 (queues), Caddy 2 (HTTPS) |
| HTTPS certificate | Let's Encrypt, issued and renewed automatically by Caddy |
| Database size | 27 MB |
| Public sign-up | **Off**: people join only with an invite link |
| Separate from | Rishi's own Real Estate CRM (`twenty-crm`, another server). The two share nothing |

## 2. How the content was made

Aroosh's CRM runs on her MacBook. Its database (every record, user and setting) has not been exported yet, so the
cloud copy was **rebuilt from her two documents** (in `docs/aroosh/`) with `scripts/build_from_docs.py`.
When her export file arrives, `scripts/import-export.sh` replaces everything with her exact data (see
[DEPLOYMENT.md](../DEPLOYMENT.md), Way A).

## 3. Data model (same as her documents)

| Object | Fields | Links |
|---|---|---|
| **People** (built-in) + retail fields | Loyalty ID; Customer Type (Retail, Wholesale, VIP); Preferred Channel (Phone, Email, Chat, SMS, Store) **(options assumed: her docs only say "contact channel options")** | Company |
| **Companies** (built-in) | standard fields | |
| **Tickets** (Retail) | Reference Number; Status (Open, In Progress, Resolved, Closed); Priority (Low, Medium, High, Urgent); Category (Order Issue, Return / Refund, Delivery, Product Inquiry, Complaint); Channel (Phone, Email, Chat, Store); Order Number; Description; Team (Support, Billing, Logistics, Escalations); First Response Due; Resolution Due; SLA Status (On Track, At Risk, Breached) | Contact (person), Account (company), Assignee (member), Interactions |
| **Service Requests** (generic, any industry) | Reference Number; Sector (Retail, Health, Real Estate, Banking, Government); Category (free text); Sub Category (free text); Description; Status; Priority; Channel (Phone, Email, Chat, SMS, Web, In Person); External Reference; First Response Due; Resolution Due; SLA Status | Contact, Account, Assignee, Interactions |
| **Catalog Entries** | Name; Sector; Category; Sub Category | stands alone: the lists for dependent dropdowns |
| **Interactions** | Type (`interactionType` in the API: Call, Email, Chat, SMS); Direction (Inbound, Outbound); Occurred At; Duration Seconds; Summary; Outcome (Resolved, Follow-up Needed, Escalated) | Ticket, Service Request, Contact, Handled By (member) |

The API names and values are the ones in her API guide (for example `referenceNumber`, `ORDER_ISSUE`,
`serviceRequests`, `catalogEntries`), so her `curl` examples work unchanged against the live address.

## 4. Records

| Type | Count | Records |
|---|---|---|
| Company | 1 (+6 automatic) | Urban Wear Boutique. Twenty adds 5 sample companies to every new workspace (Airbnb, Anthropic, Figma, Notion, Stripe), as on her laptop, and its built-in automation "Create company when adding a new person" made one called `example.com` from the contacts' email addresses. The extra ones can be deleted |
| People | 7 (+5 Twenty samples: Brian Chesky, Dario Amodei, Dylan Field, Ivan Zhao, Patrick Collison) | Fatima Khan (LOY-1002, phone 501112222), Yumna Khan, Lena Tanzil, Noor Saleh (LOY-1004, Store Manager, VIP), Ally Jayne (LOY-1005), Sam Rivers (LOY-1006, 506665555), QA PermissionTest. Her docs give no email or loyalty ID for Yumna and Lena, so those are empty |
| Tickets | 14 | TKT-0001 to TKT-0006 (her sample tickets, all linked to their contact and Urban Wear Boutique), TKT-0007, TKT-0013, TKT-0014, TKT-0015, TKT-0016, TKT-0020 (SLA breached), TKT-0030, TKT-QA-002 |
| Notes | 2 | "Phone follow-up" on TKT-0004 and on TKT-QA-002 |
| Catalog Entries | 20 | All 20 from her documents, exact (5 sectors × 2 categories × 2 sub-categories) |
| Service Requests | 4 | SR-0001 (Banking, exact payload from her docs), SR-0002 (Retail, Noor Saleh, Urban Wear Boutique), SR-0003 (Banking, Urgent), "testing record 1" (Health) |
| Interactions | 12 | The 8 on TKT-0001 to TKT-0006, "Test call" on TKT-0030, and 3 on SR-0001 and SR-0002 |
| Roles | 4 for people | Admin and Member (come with Twenty), **Agent** (see and edit, no delete), **Supervisor** (see, edit and delete). The list also shows Twenty's two system roles, "Standard role" and "Workspace Custom Application": leave them alone |

**Assumed values** (her documents did not state them; they follow her own patterns):
- Ticket categories of TKT-0001 to TKT-0006 (Order Issue, Return / Refund, Delivery), and order numbers ORD-5001, ORD-5003 to ORD-5005.
- The titles of TKT-0014, TKT-0015, TKT-0016 ("Workflow test: high / low / urgent priority").
- SR-0003's title and category ("Card blocked abroad", Cards / Card blocked); the reference `SR-0000` for "testing record 1".
- Dates, durations and summaries of the interactions, except "Wrong size call" (exact from her API guide).
- Note texts.

## 5. Not on the live copy yet

| Missing | Why | How it gets fixed |
|---|---|---|
| About 6 tickets and some test records | Her documents mention "about 20 tickets" but describe only these 14 | Her export file |
| Her and her test agent's original logins, her API keys (including Umaima's earlier key) | Passwords and keys live only in her database | Her export file. Until then: new invites and new keys |
| Workflows: "High priority ticket email", "High priority service request email", "SLA breach escalation" | They send emails, and no mailbox is connected yet | Connect a mailbox (Settings → Accounts), then rebuild them, or her export file (it contains them) |
| Mailbox (test Gmail) | Needs the Gmail app password, which only Aroosh has | Aroosh connects it herself, or her export file |
| Role "API Integration" (limited key for INVOQ) | Its object-by-object rules are set in the screen | Her export file, or set it up in Settings → Roles (her history doc, section 23) |
| Assignee / Handled By on records | Those point to people who are members; Aroosh had not joined yet | Set them in the screen, or her export file |
| Iframe embedding for INVOQ | Waiting for INVOQ's agent-screen address | Settings → General → Security → Iframe embedding |
| Automatic backups | Not set up yet | Planned next (see [OPERATIONS.md](OPERATIONS.md), "Backups") |

## 6. People with access (19 Nov 2026)

| Person | Role |
|---|---|
| Rishi Upadhyay | Admin (created the workspace) |
| Umaima Suleman | Supervisor |
| Aroosh Ahmed | Admin once she joins (she keeps building the CRM here) |
