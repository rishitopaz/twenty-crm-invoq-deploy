# Twenty CRM Project: Complete History, Current State and Next Steps

**Owner:** Aroosh Ahmed (Topaz PS-II internship)
**Team lead:** Umaima Suleman
**Last updated:** 16 November 2026 (covers work up to 13 November 2026)
**Changes in this version:** new sections 21 to 25 (INVOQ build on the Retail Tickets, the generic Service Request module, the limited API Integration role, Umaima's login, UI quirks); sections 1, 3, 11, 14, 15, 16, 17 and 18 updated; Retail demo warning added in sections 7 and 9. Nothing was removed.

This file is meant to be read on its own. It explains what the project is, everything that has been done, how to run and demo it, what was learned from research, and what is left to do. It contains no API key. Where a key is needed, the commands use a placeholder.

---

## Contents

1. [Summary and current status](#1-summary-and-current-status)
2. [People and context](#2-people-and-context)
3. [Timeline](#3-timeline)
4. [Concepts you need to understand](#4-concepts-you-need-to-understand)
5. [The system: what is installed and where](#5-the-system-what-is-installed-and-where)
6. [Installation steps and the problems that were fixed](#6-installation-steps-and-the-problems-that-were-fixed)
7. [The Retail configuration (what was built)](#7-the-retail-configuration-what-was-built)
8. [The API: what was tested](#8-the-api-what-was-tested)
9. [Demo guide: preparation, practice and live script](#9-demo-guide-preparation-practice-and-live-script)
10. [Prepared answers to likely questions](#10-prepared-answers-to-likely-questions)
11. [Documents produced](#11-documents-produced)
12. [New requirements from Umaima (the INVOQ use case)](#12-new-requirements-from-umaima-the-invoq-use-case)
13. [Research findings](#13-research-findings)
14. [Proposed design for INVOQ](#14-proposed-design-for-invoq)
15. [To-do list and open questions](#15-to-do-list-and-open-questions)
16. [Troubleshooting and gotchas](#16-troubleshooting-and-gotchas)
17. [What is not verified](#17-what-is-not-verified)
18. [External access for Umaima (Cloudflare Quick Tunnel)](#18-external-access-for-umaima-cloudflare-quick-tunnel)
19. [Iframe embedding (screen pop)](#19-iframe-embedding-screen-pop)
20. [References](#20-references)
21. [INVOQ build on the Retail Tickets (9 to 11 November)](#21-invoq-build-on-the-retail-tickets-9-to-11-november)
22. [Generic Service Request module (11 to 13 November)](#22-generic-service-request-module-11-to-13-november)
23. [API access update: the API Integration role (12 to 13 November)](#23-api-access-update-the-api-integration-role-12-to-13-november)
24. [Umaima's login to the CRM (13 Nov)](#24-umaimas-login-to-the-crm-13-nov)
25. [Twenty UI quirks and lessons from the build](#25-twenty-ui-quirks-and-lessons-from-the-build)

---

## 1. Summary and current status

**The project in one paragraph.** Umaima asked the intern team to look at Twenty, an open-source CRM, learn what it does, install it on their laptops and configure it for a business domain (one intern took Real Estate, Aroosh took Retail). The configuration needed Contacts, Accounts/Organizations and a domain-suited Ticketing module, plus API access for searching contacts, adding and updating contacts, creating tickets, searching tickets by date or reference number, and adding notes to tickets. That is built and tested. After a first meeting, Umaima extended the task: treat Twenty as if it were being used by INVOQ (storing ticket history, agent call history and all interaction history, handling emails, and automating actions), and write API documentation she can keep. After that she asked for temporary external access to the API (done through a Cloudflare Quick Tunnel) and for a way to allow Twenty to be embedded as a screen pop (found and tested).

**Status at a glance**

| Item | Status |
|---|---|
| Twenty installed locally with Docker Compose | Done |
| Contacts (People), Accounts (Companies) | Done, with retail fields on People |
| Ticketing module (custom Tickets object) | Done, linked to a contact and an account |
| API: all five required operations | Done and tested |
| Demo script, practice run | Done |
| API documentation file for Umaima (`twenty-crm-retail-api.md`) | Written and tested on 5 Nov; updated 16 Nov with sections 13 to 18 for the new objects, automations, roles and outside access (section 11) |
| Update messages to Umaima | Sent: after the meeting (6 Nov); the Service Request module, the tunnel address change and a Retail feature summary (13 Nov). She answered "yea you can apply" to applying the Retail features to the generic modules (section 22) |
| External access for Umaima (Cloudflare Quick Tunnel, limited API key) | Working. Her key was moved to the narrow **API Integration** role on 13 Nov and tested; the tunnel address has changed after a laptop sleep (sections 18 and 23). Key expires about 20 Nov |
| Iframe embedding for the screen pop | Twenty's built-in allowed-origins setting found and tested locally; the test origin was removed on 9 Nov; waiting for the INVOQ host address (section 19) |
| INVOQ extensions on the Retail Tickets: email workflow, Assignee and Team, roles, SLA fields and breach workflow, Interaction history | **Built and tested** (9 to 11 Nov, section 21). Agent object not built (workspace members are used). Comparison write-up not written |
| Generic **Service Request** module (Umaima's request of 11 Nov): Sector, free-text Category and SubCategory, dependent lists from a catalog | **Built and tested** (12 to 13 Nov, section 22). Retail features applied to it on 13 Nov; the SLA breach workflow for it is not confirmed |
| Umaima's login to the CRM | Invitation sent 13 Nov; role and Invite by link still to be checked (section 24) |

---

## 2. People and context

- **Aroosh Ahmed:** the intern doing the Retail configuration. Interning at Topaz (PS-II). Works on other tasks in parallel (QA testing of the INVOQ product).
- **Umaima Suleman:** team lead who assigned the project and receives the demo and documentation.
- **Co-intern (Real Estate):** another intern doing the same task for the Real Estate domain. Their project is used as a benchmark in section 13.
- **INVOQ:** the contact center product Aroosh and the team work with at Topaz. The newest task asks Aroosh to imagine being INVOQ and use Twenty as its CRM.

Umaima's original instruction (paraphrased): read about Twenty, install and configure it, build modules for your domain if the out-of-the-box ones do not cover it, have Contacts, Accounts/Organizations and a Ticketing module, and be able to use the API to do five things:

1. Search contact(s) by phone, email or any unique identifier.
2. Add or update a contact.
3. Create a ticket.
4. Search tickets by date or reference number.
5. Add a note to an existing ticket.

---

## 3. Timeline

Dates are the days the work happened. Times are Dubai time unless marked UTC.

| When | What happened |
|---|---|
| 27 Oct 2026 | Task received from Umaima. Concepts explained. Docker Desktop installed; Twenty installed with Docker Compose. First start failed (server unhealthy) and was fixed by adding `ENCRYPTION_KEY` to `.env`. Workspace created. Tickets custom object set up with its fields and relations. Retail fields added to People. Sample contacts, companies and tickets created. API key created. All five API operations tested with `curl`. Cheat sheet document created. |
| 30 Oct 2026 (early hours) | Docker had been restarted, so Twenty was started again. Ticket searches by reference number and by date re-verified. Account and Channel filled in on all tickets. Practice run started with a new contact (Ally Jayne, TKT-0005). The notes document was expanded into a full guide with a Do/Say demo script (live demo records: Abby Moore, LOY-1007, TKT-0007). Practice run with Sam Rivers (LOY-1006, TKT-0006) completed. Concept questions and prepared answers written. |
| First meeting with Umaima | Aroosh showed and explained the setup (contacts, accounts, tickets). Umaima asked for API documentation and set the new INVOQ requirements (section 12). |
| 4 Nov 2026 | Aroosh wrote down the new requirements from the meeting (section 12). |
| 5 Nov 2026 | Research on emails, workflows, SLA, roles, integrations and comparison with Salesforce and Freshdesk (section 13). Update message to Umaima drafted. API documentation file written. Every call in it was then tested with throwaway records, which were deleted afterwards. Section 12 of the API file was reworded. Co-intern's project reviewed as a benchmark. This history file written. |

| When | What happened |
|---|---|
| 5 Nov 2026 (later) | Umaima asked for external access to the local Twenty so she can call its API (Cloudflare or anything free). `cloudflared` installed. Two options sent to her (quick tunnel without a domain, or a named tunnel with Cloudflare Access which needs a domain); she chose the quick tunnel. She also asked to check how to allow Twenty to be embedded in an iframe as a screen pop; found that Twenty blocks it by default. |
| 6 Nov 2026 | Found Twenty's built-in **Iframe embedding** setting and verified it locally. Created the **External API access** role and the **Umaima external** API key (15-day expiry), tested the five operations locally with that key, started the Cloudflare Quick Tunnel, verified the public URL from outside, and sent Umaima the URL (key sent separately). Aroosh wrote project notes on this, which are included in section 18. |


**Timeline continued (9 to 13 November 2026)**

| When | What happened |
|---|---|
| 9 Nov 2026 | Iframe test cleaned up (allowed origin removed, Invite by link turned off). A test Gmail account was connected to Twenty by IMAP/SMTP (it saved once the SMTP port was set to 465). Workflow **High priority ticket email** built and tested (API-created tickets fire it; tickets created by hand do not). **Team** and **Assignee** added to Tickets (Assignee was saved with two destinations by mistake). Roles **Agent, Supervisor, Admin** created; a test member was invited and checked as Agent. Ticket and API checks on Umaima's key. |
| 10 Nov 2026 | SLA fields added; workflow **SLA breach escalation** built, tested on TKT-0020, activated at a 15-minute interval; two later scheduled runs found nothing and sent no repeat email. |
| 11 Nov 2026 | **Interaction** object created (fields, relations), the Type API name changed from `typeCustom` to `interactionType`, 8 sample interactions loaded and checked on ticket pages. Assignee deleted and recreated with a single destination (`assigneeId`). Umaima sent the new request: a generic Service Request module. |
| 12 Nov 2026 | **Service Request** and **Catalog Entry** objects built; 20 catalog entries loaded; SR-0001 and SR-0002 created through the API; Umaima's key tested on the new objects and found to be too broad. |
| 13 Nov 2026 | **API Integration** role created and assigned to Umaima's key; tests passed. Quick tunnel started, tested and then replaced by a second tunnel after the laptop slept. Module message sent to Umaima. Umaima answered "yea you can apply": SLA fields, interaction link and the priority alert workflow were applied to Service Requests (SR-0003 test). Umaima asked for a login; a Supervisor invitation was created and a link sent. |

---

## 4. Concepts you need to understand

### 4.1 CRM and Twenty

A **CRM** (Customer Relationship Management system) is a database with a screen on top, used to keep customers and every interaction with them in one shared place. **Twenty** is an open-source CRM. Open source means the code is public, so it can be run privately and customized. It has a customizable data model (you can add your own objects and fields from the UI).

Data model vocabulary:

- **Object:** a type of thing (People, Companies, Tickets).
- **Record:** one entry of an object (one person, one ticket).
- **Field:** a property of a record (email, status). Field types include text, select and relation.
- **Relation:** a link between objects. A ticket belongs to one person and one company; a person has many tickets.
- **View:** a saved way of showing records (table, kanban, filtered list).
- **Notes and Tasks:** built-in records that can attach to any other record.

### 4.2 Docker and the four containers

Twenty runs as four programs that work together. **Docker** runs them, and **Docker Compose** starts them all with one command.

| Container | Job |
|---|---|
| `server` | The web app and the API, on port 3000 |
| `worker` | Background jobs |
| `db` | PostgreSQL, where all records are stored |
| `redis` | Cache and job queues |

Data lives in Docker volumes, so stopping Twenty (`docker compose down`) keeps it. **Docker Desktop must be open** before any `docker` command works.

### 4.3 API, REST and the API key

The screen is for humans; an **API** is the same system for software. Twenty's API is **REST**: ordinary web requests to addresses called endpoints.

- **Endpoint:** an address per object, such as `http://localhost:3000/rest/people`. Twenty generates one for every object automatically, including the custom Tickets object.
- **Method:** `GET` reads, `POST` creates, `PATCH` changes only the fields sent, `DELETE` removes.
- **JSON:** the format data travels in, for example `{"customerType": "VIP"}`.
- **Id:** every record has a unique id (a UUID). Updates and links use ids, not emails.
- **Filter:** a search condition written as `field[comparator]:value`, for example `emails.primaryEmail[eq]:"x"` (email equals x). Other comparators used: `gte`, `lt`, `in`, `like`, `and(...)`.
- **API key:** a token that acts as a password for software. Every request carries it in the header `Authorization: Bearer <key>`. Anyone with the key can access the data, so it is never put in files or shown on screen. It is shown only once when created; if lost, regenerate it (the old one stops working).

### 4.4 UTC

Twenty stores times in **UTC**, the world reference time. Dubai is UTC+4. A ticket created between midnight and 4:00 AM Dubai time still has the previous day's date in UTC, so date searches use the UTC date. A trailing `Z` on a timestamp means UTC.

### 4.5 SLA

An **SLA** (Service Level Agreement) is a promised time limit for handling a ticket. The two main timers are first response time and resolution time, set per priority (for example a High ticket needs a first reply within 1 hour and a fix within 8 hours). When a target is missed or close to being missed, the system escalates, for instance by emailing a supervisor. Twenty has no built-in SLA feature as far as the documentation shows, so it would be built with due-date fields and workflows.

---

## 5. The system: what is installed and where
> **Added after 6 November:** a test Gmail account connected under Settings, Accounts; workflows (High priority ticket email, SLA breach escalation, and a priority alert for Service Requests); the Interaction, Service Request and Catalog Entry objects; the roles Agent, Supervisor, Admin and API Integration; and the Test Agent member. Sections 21 to 25 describe them.

| Item | Value |
|---|---|
| Machine | Aroosh's MacBook Air |
| Twenty folder | `~/twenty` (holds `docker-compose.yml` and `.env`) |
| Twenty URL | `http://localhost:3000` |
| REST base URL | `http://localhost:3000/rest` |
| Workspace name | Topaztel (taken automatically from the work email domain) |
| Login | Aroosh's work email, job title entered as Intern |
| API key | Named "Retail CRM", Admin role, never expires. Saved privately on the laptop. Not stored in any document |
| Docker | Docker Desktop; `docker compose` v2 |

The `.env` file holds an `ENCRYPTION_KEY`. It must be kept and not changed later, because Twenty uses it to encrypt stored data. Back it up somewhere safe.

Everything runs only on this laptop. If the laptop is closed or Docker is quit, Twenty stops; the data is kept and returns when Twenty is started again.

---

## 6. Installation steps and the problems that were fixed

### 6.1 Install steps

1. Install Docker Desktop from docker.com and open it. Wait until the engine is running. Check from Terminal:

```bash
open -a Docker
docker --version
docker compose version
```

2. Make a folder and download the two configuration files:

```bash
mkdir ~/twenty && cd ~/twenty
curl -o .env https://raw.githubusercontent.com/twentyhq/twenty/refs/heads/main/packages/twenty-docker/.env.example
curl -o docker-compose.yml https://raw.githubusercontent.com/twentyhq/twenty/refs/heads/main/packages/twenty-docker/docker-compose.yml
```

3. Add an encryption key to `.env` (the example file does not include one):

```bash
printf '\nENCRYPTION_KEY=%s\n' "$(openssl rand -base64 32)" >> .env
```

4. Start Twenty, wait for the server to be healthy, then open it and create the workspace:

```bash
cd ~/twenty
docker compose up -d
docker compose ps
open http://localhost:3000
```

### 6.2 Daily start and stop

```bash
open -a Docker              # wait until the engine is running
cd ~/twenty
docker compose up -d        # start
docker compose ps           # check; the server should show "healthy" (1 to 2 minutes)
docker compose down         # stop (data is kept)
```

### 6.3 Problems hit and their fixes

| Problem | Cause | Fix |
|---|---|---|
| Server container "unhealthy" on first start; log said it could not derive the session cookie secret | No `ENCRYPTION_KEY` in `.env` | Run the `printf` command in step 3, then `docker compose down` and `docker compose up -d` |
| "failed to connect to the docker API" | Docker Desktop was not running (after a restart) | Open Docker Desktop, wait for the engine, then `docker compose up -d` |
| API key lost | It is shown only once | Settings, Developers, API Keys: click the key, regenerate it, copy the new one and export it again |
| `STORAGE_S3_*` and `FALLBACK_ENCRYPTION_KEY` warnings | Optional settings not used locally | Harmless; ignore |
| A search returned nothing right after midnight Dubai time | Dates are in UTC | Use the UTC date in the filter |

---

## 7. The Retail configuration (what was built)
> **Update (13 Nov):** the Tickets object has gained Assignee, Team, First Response Due, Resolution Due and SLA Status, and a linked Interaction history. See section 21. The ticket count used in this section is out of date (test records were added, section 21.9).

### 7.1 Overview

| Requirement | How it was built |
|---|---|
| Contacts | Twenty's built-in **People** object, extended with retail fields |
| Accounts / Organizations | Twenty's built-in **Companies** object |
| Ticketing module | A **custom object** called Tickets (Twenty has no ticket object out of the box) |
| Notes | Built-in Notes, attached to records through "note targets" |

### 7.2 Extra fields on People

| Field | Type | Values |
|---|---|---|
| Loyalty ID | Text | Unique customer identifier used for lookups (for example `LOY-1002`) |
| Customer Type | Select | `RETAIL`, `WHOLESALE`, `VIP` |
| Preferred Channel | Select | Contact channel options |

Default fields used for search: Emails (`emails.primaryEmail`) and Phones (`phones.primaryPhoneNumber`, stored without the country code).

### 7.3 The Tickets custom object

| Field | Type | Values / notes |
|---|---|---|
| Name | Text | Ticket subject |
| Reference Number | Text | For example `TKT-0007`. Typed by the caller; not auto-generated; no uniqueness rule is configured |
| Status | Select | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| Priority | Select | `LOW`, `MEDIUM`, `HIGH`, `URGENT` |
| Category | Select | `ORDER_ISSUE`, `RETURN_REFUND`, `DELIVERY`, `PRODUCT_INQUIRY`, `COMPLAINT` |
| Channel | Select | `PHONE`, `EMAIL`, `CHAT`, `STORE` |
| Order Number | Text | For example `ORD-5007` |
| Description | Text | Free text |
| Contact | Relation | Belongs to one Person (API field `contactId`); each Person lists their Tickets |
| Account | Relation | Belongs to one Company (API field `accountId`); each Company lists its Tickets |

In the UI the select options show friendly labels; in the API they are uppercase with underscores.

### 7.4 Relationship picture

```
Company (Account) 1 ----< Person (Contact) 1 ----< Ticket >---- 1 Company (Account)
                                                      |
                                                      +----< NoteTarget >---- Note
```

A note is its own record. A "note target" links it to a person, company or ticket, so one note can be attached to several records.

### 7.5 Sample data currently in the workspace

| Contacts | Notes |
|---|---|
| Fatima Khan (LOY-1002, phone 501112222, belongs to Urban Wear Boutique), Yumna Khan, Lena Tanzil, Noor Saleh (LOY-1004, created through the API), Ally Jayne (LOY-1005, created through the API), Sam Rivers (LOY-1006, practice) | Notes attached to the tickets below (for example "Phone follow-up" on Wrong size delivered, created through the API) |

| Ticket | Subject | Contact | Status / priority / channel |
|---|---|---|---|
| TKT-0001 | Damaged item received | Fatima Khan | Open / High / Phone |
| TKT-0002 | Refund not received | Yumna Khan | In Progress / Medium / Chat |
| TKT-0003 | Where is my delivery? | Lena Tanzil | Open / Low / Store |
| TKT-0004 | Wrong size delivered | Noor Saleh | Open / High / Phone |
| TKT-0005 | Missing item in order | Ally Jayne | Open / Medium / Email |
| TKT-0006 | Late delivery (practice) | Sam Rivers | Open / High / Phone |

All tickets are linked to the account Urban Wear Boutique. After the live demo creates TKT-0007, there are 7 tickets.

The five default companies and eight default contacts that Twenty creates in a new workspace (Airbnb, Anthropic, Stripe, Figma, Notion and their people) are sample data from Twenty itself.

---

## 8. The API: what was tested

Tested means run against this installation. All five required operations work, and a large set of extra calls was tested on 5 November with throwaway records that were then deleted.

| Area | Verified |
|---|---|
| Contacts | Search by email, phone and loyalty ID; add; update; get by id; link to a company; delete |
| Accounts | List; search by name; add; update; delete |
| Tickets | Create (with contact and account); search by reference number, by date and by date range; by contact; combined filter; update status; newest-first ordering; pagination; delete |
| Notes | Create; link to a ticket, a contact and a company; delete |

Not yet tested: preventing duplicate records, how the API responds to an invalid select value, and reading back the notes attached to a record.

### 8.1 Behaviors worth knowing

- **Response shapes:** a list comes back as `{"data": {"people": [...]}, "totalCount": n, "pageInfo": {...}}`; a create or update as `{"data": {"createPerson": {...}}}`; get-one under `data.person` (singular); a delete as `{"data": {"deleteNote": {"id": "..."}}}` with HTTP 200.
- **Pagination:** `limit` (maximum 60), then `starting_after=<endCursor>` for the next page. Without `order_by`, results are not in date order (cursors are based on the record id), so add `order_by=createdAt[DescNullsLast]` when order matters.
- **Dates and phones:** dates are UTC; phones are searched without the country code.
- **The API does not stop you creating duplicates by itself that was tested; search before adding.** (Duplicate prevention was not tested.)

### 8.2 Command reference

Run these in one Terminal window. First start Twenty and set the key (see section 9.1 for the full preparation). The commands use `$TWENTY_API_KEY`, which must be set in that window.

**Set the key** (paste the saved key; never write it in a file):

```bash
export TWENTY_API_KEY="PASTE_KEY_HERE"
```

**Helper functions** (optional; print one clean line per record instead of raw JSON, window-only so paste them again in each new window; they only work on search and list responses):

```bash
show_people() { python3 -c "import sys,json; [print(p['name']['firstName'], p['name']['lastName'], '|', p['emails']['primaryEmail'], '|', p['loyaltyId'], '|', p['customerType']) for p in json.load(sys.stdin)['data']['people']]"; }
show_tickets() { python3 -c "import sys,json; d=json.load(sys.stdin); [print(t['referenceNumber'], '|', t['name'], '|', t['status'], '|', t['priority'], '|', t['channel']) for t in d['data']['tickets']]; print('Total:', d['totalCount'])"; }
```

**Check the key works** (prints the first 8 characters, then the start of a ticket):

```bash
echo ${TWENTY_API_KEY:0:8}
curl -s -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/tickets?limit=1" | python3 -m json.tool | head -5
```

**How a command is built** (`curl` sends a web request):

| Part | Meaning |
|---|---|
| `-s` | Quiet; no progress bar |
| `-G` | Put the data in the address as a search |
| `-X POST` / `-X PATCH` | Create / update (the method) |
| `-H "Authorization: Bearer $TWENTY_API_KEY"` | Your login |
| `-H "Content-Type: application/json"` | The data you send is JSON |
| `"http://localhost:3000/rest/people"` | Which object |
| `--data-urlencode 'filter=...'` | The search condition, safely encoded |
| `-d '{...}'` | The data to create or change |
| `$(...)` and `VAR=...` | Run a command and save its result in a variable, valid only in that window |
| `\| python3 -m json.tool` | Format the reply to be readable |
| `\| show_people` / `\| show_tickets` | Print one clean line per record |

The other commands are given in the demo script (section 9.4), which uses new records. For the same calls with sample outputs, the API documentation file (section 11) is the full reference.

---

## 9. Demo guide: preparation, practice and live script
> **Warning (13 Nov):** the live demo creates **TKT-0007**, but a test ticket ("Workflow email test 2") already uses that reference. Use a different reference for the live ticket, or rename or delete the test ticket first. Ticket counts quoted below (for example 7 tickets) no longer match; there are about 20 tickets now (section 21.9). The workspace also now has Interactions, Service Requests and Catalog Entries in the left menu.

### 9.1 Preparation (5 to 10 minutes before)

1. Start Docker and Twenty and wait for the server to be healthy:

```bash
open -a Docker
cd ~/twenty
docker compose up -d
docker compose ps
```

2. In a fresh Terminal window, set the key and paste the two helper functions (section 8.2). Check the key:

```bash
echo ${TWENTY_API_KEY:0:8}
```

3. Open Twenty on the Tickets table and log in if asked:

```bash
open http://localhost:3000/objects/tickets
```

4. Keep the API documentation or this file open to follow. Never show the key on screen. Do not run any add or create command as a test, because that uses up the live demo records.

### 9.2 Quick health check (any time before the demo)

```bash
cd ~/twenty
docker compose ps
echo ${TWENTY_API_KEY:0:8}
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/people" --data-urlencode 'filter=loyaltyId[eq]:"LOY-1002"' | show_people
```

Expected: the server shows healthy, the key prints its first 8 characters, and the search prints `Fatima Khan | fatima.khan@example.com | LOY-1002 | RETAIL`. Then refresh the Twenty tab and check you are still logged in.

### 9.3 Practice versus live records

| | Practice | Live demo |
|---|---|---|
| Contact | Sam Rivers | Abby Moore |
| Email | sam.rivers@example.com | abby.moore@example.com |
| Phone | 506665555 | 508887777 |
| Loyalty ID | LOY-1006 | LOY-1007 |
| Ticket | TKT-0006 | TKT-0007 |
| Order | ORD-5006 | ORD-5007 |

The practice run has been done. Do not reuse Sam Rivers or TKT-0006 in the live demo. There are now two tickets with a similar name ("Late delivery..."); when opening a ticket at the end, check the reference number is TKT-0007 and the contact is Abby Moore. Variables such as `$PERSON_ID` and `$TICKET_ID` do not carry over between Terminal windows, so use a fresh window and set the key again.

### 9.4 Live demo script (with what to say)

Run the steps in order. Read the **Say** lines in your own words.

**Step 1: Set the scene (browser)**
Do: show the Tickets table.
Say: This is Twenty, an open-source CRM that I run locally in Docker. I configured it for the Retail domain. People are our Contacts, Companies are our Accounts, and I built a custom Tickets object that links to both.

**Step 2: Show the ticket module (browser)**
Do: open the ticket "Wrong size delivered" and point at Reference Number, Status, Priority, Category, Channel, Order Number, Contact, Account and the note.
Say: Each ticket has a reference number, status, priority, category, channel and order number. It belongs to one contact and one account, and notes attach to it.

**Step 3: Show the contact fields (browser)**
Do: open People, click Fatima Khan, and point at Loyalty ID, Customer Type and her Tickets.
Say: Contacts carry retail fields: a loyalty ID, a customer type and a preferred channel. Each contact lists their tickets.

**Step 4: Search a contact by email, phone and loyalty ID (Terminal)**

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/people" --data-urlencode 'filter=emails.primaryEmail[eq]:"fatima.khan@example.com"' | show_people
```

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/people" --data-urlencode 'filter=phones.primaryPhoneNumber[eq]:"501112222"' | show_people
```

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/people" --data-urlencode 'filter=loyaltyId[eq]:"LOY-1002"' | show_people
```

Each prints `Fatima Khan | fatima.khan@example.com | LOY-1002 | RETAIL`.
Say: Through the API I can find a customer by email, by phone number, or by any unique identifier such as the loyalty ID. All three return the same person.

**Step 5: Add a new contact (Terminal, then browser)**

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" -H "Content-Type: application/json" "http://localhost:3000/rest/people" -d '{
  "name": {"firstName": "Abby", "lastName": "Moore"},
  "emails": {"primaryEmail": "abby.moore@example.com"},
  "phones": {"primaryPhoneNumber": "508887777", "primaryPhoneCountryCode": "AE", "primaryPhoneCallingCode": "+971"},
  "loyaltyId": "LOY-1007",
  "customerType": "RETAIL"
}' | python3 -m json.tool | head -12
```

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/people" --data-urlencode 'filter=emails.primaryEmail[eq]:"abby.moore@example.com"' | show_people
```

Then open and refresh the People page (`open http://localhost:3000/objects/people`). Abby Moore appears, and Created by shows "Retail CRM".
Say: A new customer comes in, so I create her through the API. She appears in the UI straight away, and Created by shows Retail CRM, which proves the record came through the API key.

**Step 6: Update the contact (Terminal)**

```bash
PERSON_ID=$(curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/people" --data-urlencode 'filter=emails.primaryEmail[eq]:"abby.moore@example.com"' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['people'][0]['id'])")
echo $PERSON_ID
```

```bash
curl -s -X PATCH -H "Authorization: Bearer $TWENTY_API_KEY" -H "Content-Type: application/json" "http://localhost:3000/rest/people/$PERSON_ID" -d '{"customerType": "VIP"}' | python3 -m json.tool | grep customerType
```

Expected: `"customerType": "VIP",`
Say: To update a contact I find the record by email, then patch only the field that changes. Abby is now a VIP customer.

**Step 7: Create a ticket (Terminal)**

```bash
TICKET_ID=$(curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" -H "Content-Type: application/json" "http://localhost:3000/rest/tickets" -d '{
  "name": "Late delivery complaint",
  "referenceNumber": "TKT-0007",
  "status": "OPEN",
  "priority": "HIGH",
  "category": "DELIVERY",
  "channel": "PHONE",
  "orderNumber": "ORD-5007",
  "description": "Order has not arrived on the promised date.",
  "contactId": "'"$PERSON_ID"'"
}' | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['data']['createTicket']['id'] if 'data' in r else r)")
echo $TICKET_ID
```

It prints a ticket id (a UUID).
Say: Abby calls about a late delivery, so I open a ticket linked to her. It has a reference number, a priority, a category and the order number.

**Step 8: Search tickets by reference number (Terminal)**

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/tickets" --data-urlencode 'filter=referenceNumber[eq]:"TKT-0007"' | show_tickets
```

Expected: `TKT-0007 | Late delivery complaint | OPEN | HIGH | PHONE` and `Total: 1`.
Say: Agents can pull up a ticket instantly by its reference number.

**Step 9: Search tickets by date (Terminal)**

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/tickets" --data-urlencode 'filter=createdAt[gte]:"2026-10-27T00:00:00.000Z"' | show_tickets
```

```bash
curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/tickets" --data-urlencode 'filter=createdAt[gte]:"2026-11-05T00:00:00.000Z"' | show_tickets
```

The first lists every ticket (7 after TKT-0007 is created). The second should show only tickets created on or after the date in it. Change the date in the second command to the current UTC date (or the day before if it shows `Total: 0`, because Dubai is four hours ahead of UTC).
Say: The date filter returns every ticket created on or after a date, so I can narrow from all tickets down to just today's. Dates are stored in UTC.

**Step 10: Add a note to the ticket (Terminal, then browser)**

```bash
NOTE_ID=$(curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" -H "Content-Type: application/json" "http://localhost:3000/rest/notes" -d '{"title": "Phone follow-up", "bodyV2": {"markdown": "Customer called about the delay. New delivery date confirmed."}}' | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['data']['createNote']['id'] if 'data' in r else r)")
echo $NOTE_ID
```

```bash
curl -s -X POST -H "Authorization: Bearer $TWENTY_API_KEY" -H "Content-Type: application/json" "http://localhost:3000/rest/noteTargets" -d '{"noteId": "'"$NOTE_ID"'", "targetTicketId": "'"$TICKET_ID"'"}' | python3 -m json.tool | head -8
```

Then open the Tickets page (`open http://localhost:3000/objects/tickets`), click the ticket for Abby (reference TKT-0007), and show the note in its Notes section.
Say: A note is its own record, so I create it and then link it to the ticket. It shows up on the ticket right away, and it can attach to any other record the same way.

The note attaches to whichever ticket id is stored in `$TICKET_ID`, which Step 7 sets. To attach a note to a different existing ticket, look up its id by reference number and save it first:

```bash
TICKET_ID=$(curl -s -G -H "Authorization: Bearer $TWENTY_API_KEY" "http://localhost:3000/rest/tickets" --data-urlencode 'filter=referenceNumber[eq]:"TKT-0004"' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['tickets'][0]['id'])")
echo $TICKET_ID
```

**Step 11: Close**
Say: That covers everything on the list: searching contacts by email, phone and unique ID, adding and updating a contact, creating a ticket, searching tickets by date and reference number, and adding a note. All of it runs through one REST API key, so a contact center system could look up a caller by phone number and open a ticket the same way.

If a command errors in front of people, stay calm and say you will check the field name. The REST playground (Settings, Developers, Launch) shows exact field names and filter syntax.

### 9.5 Practice swaps

To practise again, run the same steps with the practice records from the table in 9.3 (this will create new records, so use fresh details such as LOY-1008 and TKT-0008 rather than reusing Sam Rivers or TKT-0006).

### 9.6 What not to run casually

- The "add contact" and "create ticket" commands in older notes (Noor Saleh, TKT-0004), because those records already exist and would be duplicated.
- `docker compose down` before a demo (it stops Twenty).
- Regenerating the API key (it makes the saved key stop working).
- Re-running the `ENCRYPTION_KEY` command if `.env` already contains one.
- Renaming or deleting Fatima Khan, the ticket "Wrong size delivered", the company Urban Wear Boutique, or any select option names, because the demo steps depend on them.

Changes made in the browser appear in the next API call, and records created through the API appear in the browser after a refresh. Both read the same database.

---

## 10. Prepared answers to likely questions

**Brief overview of what you built.**
Twenty is an open-source CRM that I installed and run locally using Docker. I configured it for the Retail domain. Contacts are customers, with retail fields like loyalty ID and customer type. Accounts are the business customers. I also built a custom ticketing module for retail issues like wrong items and late deliveries, with a reference number, status, priority, category, channel and order number. Then I tested the API: I can search contacts by email, phone or loyalty ID, add and update contacts, create tickets, search tickets by date or reference number, and add notes to a ticket.

**What is a REST API?**
It is a way for other software to talk to Twenty over the web, without using the screen. I send a request to an address like `/rest/people`, and Twenty sends back the data in JSON format. The type of request says what I want: GET to read, POST to create, PATCH to update.

**What is your REST API here?**
It is Twenty's built-in API, running on my laptop at `localhost:3000/rest`. I did not write it from scratch. Twenty generates it automatically for every object in the data model, including the custom Tickets object I built, so as soon as I created Tickets it got its own endpoint. I use it to do everything the UI does. Each request carries my API key.

**Did you build the API?**
No, Twenty provides it. What I built is the Retail configuration on top of it: the ticketing object, its fields and relations, and the retail fields on contacts. The API exposes all of that automatically.

**What is your key?**
It is an API key that I created in Twenty's settings with an Admin role. Every request carries it, and Twenty uses it to check that the request is allowed. It works like a password for software, so I keep it private and do not put it in files.

**How is it all linked?**
Everything lives in one database inside Twenty, and both the browser and the API read and write the same data. A ticket is linked to one contact and one account, and a person can have many tickets. Notes are separate records that can be attached to any of them, including tickets. So a ticket created through the API shows up in the browser straight away, linked to the right customer.

**How does it run on your laptop?**
Docker runs four containers together: the Twenty server, a background worker, a PostgreSQL database that stores the data, and Redis for caching and queues. One command starts them all.

**Why did you choose Twenty?**
It is open source, I can host it and control the data, and I can add my own objects and fields from the UI. That is how I built the ticketing module, since there is no ticket object out of the box.

**How did you build the ticketing module?**
Twenty has no ticket object by default, so I created a custom object called Tickets. I added fields for reference number, status, priority, category, channel, order number and description, then linked it to People as the Contact and to Companies as the Account.

**Why does adding a note take two calls?**
A note is its own record, and a separate link record attaches it to any other record. So I create the note first, then link it to the ticket. One note can be attached to people, companies or tickets this way.

**Why did the date search miss a ticket?**
Twenty stores dates in UTC, and Dubai is four hours ahead. A ticket created just after midnight in Dubai still has the previous UTC date, so the filter needs that date.

**What are the limitations?**
The reference number is a plain text field that I fill in, so Twenty does not generate it and no uniqueness rule is configured. There is also no assignment, SLA or ticket lifecycle logic out of the box. It is a local, single-workspace setup, not production hosting.

**What would you do next?**
Auto-generate reference numbers, add a workflow for assigning tickets and changing status, and connect an external system, such as a contact center, through the API or webhooks.

**Where does the data live?**
In the Postgres container, on a Docker volume on my laptop.

**Do you need to code something that is not in Twenty?**
Yes for some INVOQ-specific parts, but not by changing Twenty's source code. There are three levels: no code (data model, views, roles, workflows built in the UI), low code (workflow Code and HTTP actions), and real code (Twenty apps with logic functions, or outside services that use the REST API). Code would be needed for loading call history from INVOQ's phone system, round-robin or least-busy agent assignment, SLA timers, and email-to-ticket if no built-in option exists.

If a question is not known, it is fine to say it needs checking, and show the REST playground.

---

## 11. Documents produced

| Document | What it is | Status |
|---|---|---|
| **Notes document** (a Claude Doc titled "Twenty CRM (Retail) - API Cheat Sheet") | Concepts, installation, problems fixed, what was built, gotchas, the live demo script with Do/Say lines, likely questions, limitations, and a before-the-meeting checklist. Link: https://claude.ai/artifact/QSLQzqyjKggA6vDdPK4UQy | Complete. Does not yet include the INVOQ research (sections 12 to 14 here). Aroosh planned to download it as a PDF |
| **`twenty-crm-retail-api.md`** | API documentation for Umaima: authentication, conventions (filters, pagination, UTC), data model, and Contacts, Accounts, Tickets and Notes with sample requests and outputs, an end-to-end example, troubleshooting and a verification summary | All calls tested on 5 Nov. Updated 16 Nov: sections 13 to 18 added (see below) |
| **Project notes: external Twenty API access for Umaima** (written by Aroosh, 6 Nov) | Step-by-step notes on the role, key, tunnel and tests | Complete; its contents are in section 18 of this file |
| **This file** (`twenty-crm-project-history.md`) | Everything in one place | Current as of 16 Nov (work up to 13 Nov) |

### Updates to `twenty-crm-retail-api.md` (checked and extended on 16 Nov)

The three edits that were listed here on 6 Nov were checked in the file: the reworded status legend (section 1), the reworded verification summary (section 12) and Appendix A are already in it. New in this version:

- The overview table, authentication notes, base URL, data model, ticket fields, error table, "current limits" and verification summary were updated.
- New sections: **13** Interactions, **14** Service Requests (including the payload changes compared with the Retail ticket), **15** Category catalog (dependent lists by sector), **16** Automations, **17** Roles and API key permissions, **18** Using the API from outside the laptop (replace `http://localhost:3000` with the tunnel address).
- Calls not run on this deployment are labelled **Not yet tested**.

Do not paste the real API key into any document; keep the `PASTE_KEY_HERE` placeholder, and do not write a tunnel address or an invite link into it either. To share the file: save it in VS Code, attach it in Teams to the chat with Umaima, and consider also sending a PDF, because a `.md` file looks messy in plain text viewers.

---

## 12. New requirements from Umaima (the INVOQ use case)

Notes from the meeting, cleaned up:

1. Imagine you are **INVOQ** and you need to use this CRM to store **all ticket history, agent call history and all interaction history**, and to look into **emails**.
2. **Emails:** find out everything that can be done with emails in Twenty. For example, when a ticket has high priority, can it send an automatic email, without connecting to a third-party app such as Teams? Just use emails for now.
3. Find out whether **extra modules** are needed to do this, and if so what, where and how.
4. Look into **SLA** (what it means and how it applies).
5. Look into **Salesforce, Freshdesk and other CRMs**, and consider implementing Twenty in a similar way.
6. The end goal: build a CRM for INVOQ that Umaima can use for everything.
7. Produce an **API markdown document** with everything explained in the first meeting: contacts, the Tickets object, accounts (companies), sample input and sample output, as general API documentation she can keep. (Done; see section 11.)

Follow-up questions Umaima asked:

- Is there something that would need to be **coded** that is not already in Twenty's source code? (Answered in section 10 and below.)
- If a particular action happens, can it also **send an email to an agent or agents** and **create a ticket automatically**?
- Can Twenty **connect to other apps** such as Teams or Slack through connectors?
- Can it **automatically assign agents to tickets** when related to a particular thing?
- How does a CRM **manage a team**?

---

## 13. Research findings

These come from Twenty's documentation and other sources listed in section 20. Where something was not confirmed, it says so.

### 13.1 Emails in Twenty

Two separate things:

**Email sync (storing email history).** A Google Workspace or Microsoft 365 mailbox can be connected (other providers through IMAP/SMTP settings). Emails are linked automatically to the matching Company and People records, full threads show on each record's timeline, and emails can be sent from Twenty. Sync runs about every 5 minutes, and internal same-domain emails are not synced by default.

**Automatic emails from workflows.** Workflows can send emails from a connected account. This needs a mailbox connected under Settings, Accounts, with sending permissions enabled. For a local demo, a real test mailbox (for example Gmail or Outlook) is needed.

Other email uses: auto-replying to inbound emails that match certain criteria, follow-ups with a delay, and SLA warning emails to supervisors. Not found: any way for Twenty to create a ticket automatically from an incoming email (Salesforce calls this Email-to-Case). Test it before promising it.

### 13.2 Workflows (the automation engine)

A workflow has a trigger, steps and variables.

- **Triggers:** a record is created, updated, deleted or upserted; a user clicks a button (manual); a recurring schedule (cron; scheduled workflows run in UTC); or an external system sends an HTTP POST (webhook).
- **Actions:** Create, Update, Delete, Search and Upsert records; Iterator (loop over records); Filter; If/Else branches; Delay; Send Email; Code (custom JavaScript); HTTP Request (call any external API); Form (collect input). An AI Agent action is listed as coming soon.
- Variables carry data between steps, written like `{{trigger.object.fieldName}}`.
- Workflows are built in Settings, Workflows. Use the Test button with sample data, then activate.
- Code actions and HTTP requests consume more workflow credits than basic record actions.

**Recipe: high-priority ticket sends an email**

1. Settings, Accounts: connect a mailbox with send permission.
2. Create a workflow with trigger **Record is Updated or Created** on Tickets.
3. Add a **Filter** so only Priority = High (and optionally Urgent) continues.
4. Add **Send Email** to the supervisor, using variables for the subject and body (for example the reference number).
5. Test, then activate.

### 13.3 Can it auto-assign agents to tickets?

No built-in rule engine, round-robin or skills routing was found. It can be built with a workflow: trigger on Ticket created, If/Else on Category (for example Delivery goes to the delivery team), Search Records to find matching agents, Update Record to set the ticket's Assignee, then Send Email to that agent. Simple category-to-team rules need no code. Round-robin or "least busy agent" needs a Code action. An Assignee field is needed (a relation to an Agent object, or to a workspace member).

### 13.4 If an action happens, send an email and create a ticket automatically

Yes, as a standard workflow. Example: an Interaction is logged as a complaint (or INVOQ's phone system calls the workflow's webhook), then **Create Record** makes a Ticket, then **Send Email** notifies one or several agents (use a loop for several). Emails go out from the connected mailbox.

### 13.5 Connecting to Slack, Teams and other apps

No built-in Slack or Teams connector was found. Ways to connect:

- **Zapier:** a Twenty integration exists where a record being created, updated or deleted can trigger a Slack message.
- **Webhooks to n8n or Make:** for example an n8n workflow that receives a TwentyCRM webhook and posts a Slack notification.
- **The workflow HTTP Request action**, which calls an external API directly.
- Twenty also has outbound Webhooks in Settings, Developers.

Teams should work the same way (through an automation tool, or an HTTP request to a Teams webhook URL), but only Slack was confirmed.

### 13.6 Do you need to code something not in Twenty's source?

For INVOQ, yes for some parts, but not by changing Twenty's source code:

1. **No code:** data model, views, roles, workflows built in the UI.
2. **Low code:** workflow Code and HTTP Request actions.
3. **Real code:** Twenty apps can ship their own workflows and logic functions (installed as active workflows), and outside services can use the REST API.

What needs code: loading call history from INVOQ's phone system (an API script), round-robin or least-busy assignment, SLA timers, and email-to-ticket if no built-in option exists.

### 13.7 How a CRM manages a team

1. **People and roles:** who can log in and what they may do.
2. **Ownership:** every record has an owner or assignee.
3. **Teams and queues:** groups with their own workload.
4. **Routing:** rules that decide who gets a new ticket.
5. **Visibility:** views, dashboards and a history of who did what.
6. **Escalation:** SLA timers that alert a supervisor when work is late.

In Twenty: roles come as **Admin** and **Member** by default, with custom roles you can add, and one role per user. Permissions can be set per object and per field, and there is row-level filtering. Roles can also be assigned to **API keys** (Settings, Members, Roles, Assignment tab, then assign to an API key), so a reporting tool can get a read-only key. There is no native "Teams" feature; model teams with a Team object or a select field. The settings permissions cover API key generation, role assignment, data model configuration, security and workflow management.

### 13.8 SLA, Freshdesk and Salesforce compared with Twenty

- **Freshdesk:** SLA policies set time targets per priority (first response and resolution), the first matching policy applies, and reminders and escalation emails are sent when targets are at risk or missed. An example setup gives VIP customers a 1-hour response and 4-hour resolution, and high-priority issues 2 hours and 8 hours.
- **Salesforce Service Cloud:** cases are created from inbound email, web forms, phone (through CTI) or manually, and each case belongs to a Contact and usually an Account. It adds Omni-Channel routing (assign cases to available agents with the right skills and capacity) and Entitlements and Milestones to track SLA compliance with warnings.
- **Twenty:** strong at a customizable data model, workflows, email sync, an open API and roles. As far as the documentation shows, it lacks ready-made ticket lifecycle, SLA timers, routing and phone integration, so those would be built on top.

### 13.9 Benchmark: the co-intern's Real Estate project

Summary of what the co-intern built (from his whiteboard summary):

- Twenty in Docker with the same four parts, plus **their own API layer** on top that exposes the data over HTTPS so other apps can connect from anywhere.
- **Companies and Listings** (developers and agencies with their listings), **People** (buyers, sellers, owners, tenants), and a **property chain** Builder, Building, Flat, Resident, Issue (ticket). Tickets are linked to a person and a property, with notes and a history.
- **Teams and roles:** Technician, Manager and Head. Tickets are assigned to a team and a person. Everyone logs in with their own account, and the role decides what they can change. Outside viewers get view-only access.
- The admin sees the live status of every team and a timeline of everything done. **An overdue ticket automatically moves up to the Manager, then the Head.**
- Other systems use the external API with their own key; view-only keys cannot change anything.

How Retail/INVOQ compares and what to borrow:

| His feature | Retail / INVOQ version |
|---|---|
| Technician / Manager / Head roles | Agent / Supervisor / Admin; tickets get an Assignee and a Team |
| Overdue tickets escalate upward | SLA idea: Resolution Due date, a scheduled workflow checks it and emails the supervisor |
| Timeline of everything on a ticket | Notes, status changes and Interaction records on each ticket |
| Builder to Building to Flat to Resident to Issue | Store to Order to Product to Ticket (a custom Order object is the most retail-specific upgrade) |
| View-only API keys | Assign a read-only role to an API key |
| Own API layer over HTTPS | Optional; Twenty's REST API already exposes the data |

What he does not have that Umaima asked for: call, chat and email history (an Interaction object) and synced emails with automatic emails. Lead with those.

---

## 14. Proposed design for INVOQ
> **Status (13 Nov):** this design was built and tested (section 21), with these differences: no separate Agent object (workspace members are used through the Assignee and Handled By relations), and Interactions link to tickets, contacts and agents. A second, generic design for several industries was added (section 22).

**Objects**

| Object | Purpose |
|---|---|
| People, Companies, Tickets | Already built |
| **Interaction** (new) | One record per call, chat, SMS or email: type, direction, time, duration, agent, summary, plus links to the Contact and the Ticket. This is the interaction history, including call history |
| **Agent** (new) | Contact center agents who do not need a Twenty login, linked to tickets and interactions |
| Notes, Tasks, synced emails | Built in |

**New fields on Tickets:** Assignee or Agent, Team, First Response Due, Resolution Due, SLA Status, Resolved At.

**Flow to draw on the whiteboard:** channels (call, email, chat) feed an Interaction, which links to a Ticket, which is assigned to an Agent or Team, then an SLA check runs, then escalation goes to a Supervisor by email.

Call history would be pushed in through the REST API, because Twenty has no phone system of its own.

**Views worth adding (safe to add before a demo, they do not affect the API):** a kanban board of tickets by Status, an "Open and high priority" table, views by Category (Delivery, Refunds), a VIP contacts view. Do not drag cards during a live demo, because that changes a ticket's status.

---

## 15. To-do list and open questions

*Updated 16 November 2026. The 6 November list was finished or replaced; what is left is below.*

### 15.1 Immediate (as of 13 November)

1. **Umaima's login (section 24).** After she signs up through the link: set her role to Supervisor if she joined as Member, then switch **Invite by link** off, and check that signing in through the tunnel works.
2. **Service Request SLA breach workflow.** Confirm it was built (a duplicate of **SLA breach escalation** with the object switched to Service Requests), test it with an overdue request (SR-0004 was planned), then activate it (section 22.7). Also check that **Layout All Access** and **Logic All Access** are off on the API Integration role (section 23.2).
3. **Outlook delivery.** The priority alert for SR-0003 was confirmed only in the test Gmail's Sent folder; check it arrived in the Topaztel inbox once Outlook is working.
4. **Clean up test records:** delete the service requests `SR-TEST` and `SR-TEST2` created with her key, and decide about the other test records (section 21.9), especially the **TKT-0007 clash** with the demo script.
5. **Key expiry (about 20 Nov).** If she still needs the API after that, create a new key under API Integration with a 30-day expiry and send it privately. When testing ends, stop the tunnel and revoke or let the key expire.
6. **Tunnel:** keep the laptop awake with the lid open while she tests, and send her the new address after any restart (section 23.5). A named Cloudflare tunnel would give a permanent address.
7. **Waiting on Umaima:** whether INVOQ should create interactions through the API (needs an edit rule on Interactions in her role), the address of the INVOQ agent screen for the iframe (section 19), and any more changes to the generic module.
8. **Documents:** send her the updated `twenty-crm-retail-api.md` (and a PDF). Optionally add sections 12 to 14 and 21 to 22 to the notes document.
9. Before any demo, run the quick health check (section 9.2) and check the ticket count.

### 15.2 Optional improvements

- Saved views on Tickets (My Queue, Urgent and High, SLA Breached) and a supervisor dashboard; the same on Service Requests by sector.
- Show the priority in the alert email subject.
- Copy each ticket's contact onto its interactions, and put reference numbers into interaction names (or change the label used for tickets).
- Enforce catalog values on Service Requests (a workflow could flag categories that are not in the catalog) if Umaima wants it.
- Automatic assignment or routing of new requests; a first-response SLA warning email using `firstResponseDue`.
- A written comparison of Twenty, Salesforce and Freshdesk, and a design summary to present.
- Test whether a workflow can create a ticket from an incoming email, and whether a Teams message can be sent through an HTTP request.

### 15.3 Build order for INVOQ: what happened

| Step (from the 6 Nov plan) | Result |
|---|---|
| 1. Test mailbox and priority email workflow | Done (section 21.2, 21.3) |
| 2. Assignee, Team, roles | Done (21.4, 21.5) |
| 3. SLA fields and escalation workflow | Done (21.6) |
| 4. Interaction and Agent objects with sample data | Interaction done with 8 samples (21.7, 21.8); no Agent object (workspace members instead) |
| 5. Read-only API key | Replaced by the **API Integration** role for Umaima's key (23) |
| 6. Comparison and design summary | Not done |
| 7. Create a ticket from an incoming email; Teams via HTTP | Not tested |

### 15.4 Items from the 6 Nov list: outcome

| Item | Outcome |
|---|---|
| Review the External API access role | It was too broad; replaced by **API Integration** (23) |
| Decide about the QA test records | Kept; they are listed in section 21.9 |
| Clean up the iframe test | Done on 9 Nov (allowed origin removed; Invite by link turned off, and later turned back on for Umaima's invite) |
| API documentation edits and the "using the external URL" section | The edits were already in the file; sections 13 to 18 added on 16 Nov |

### 15.5 Questions for Umaima

- Which mailbox can be used for testing emails? (a dedicated test Gmail account was created and used; no answer recorded)
- How will call data reach the CRM (an API push from INVOQ's phone system)? Open; her key can currently only read Interactions.
- Do agents need their own logins, or are they just data? Open; workspace members act as agents in the current design.
- Which SLA targets does INVOQ use? Open; the demo uses an arbitrary resolution date.
- How far should this go? Partly answered: she asked for a working generic module and approved applying the Retail features to it.

---

## 16. Troubleshooting and gotchas

| Symptom | Likely cause | Fix |
|---|---|---|
| `Unauthorized` or an empty key | Key missing, wrong or regenerated | Export the current key again |
| `command not found: show_people` | Helper functions not defined in this window | Paste the two helper functions again |
| Connection refused, or the page will not load | Twenty is not running | `cd ~/twenty && docker compose up -d`, wait for healthy |
| Docker command fails with an API error | Docker Desktop not running | Open Docker Desktop, wait, then start Twenty |
| Server "unhealthy" | Missing `ENCRYPTION_KEY` or still starting | Check `docker compose logs server --tail 30`; add the key and restart if needed; otherwise wait a minute |
| Search returns nothing | Typo, or a phone search with the country code | Check spelling; search the number without the code |
| Date search misses a record | UTC versus Dubai time | Use the UTC date (or the day before) |
| A step fails after opening a new Terminal window | Variables are per window | Set the key again and re-run the lookups that set `PERSON_ID` and `TICKET_ID` |
| Duplicate records appear | The same create command was run twice | Search before creating; use new details in demos |
| `+` menu in the table does not list a field | The field is already shown, or hidden | Search the field by name in the menu, or use Options, Fields |
| Notes page shows an "Untitled" note | A note created in the UI without a title | Harmless |
| `403 Missing authentication token` on the public URL | The request reached Twenty without a key | Add the `Authorization: Bearer` header (this response also proves the tunnel works) |
| `$UMAIMA_KEY` prints length `0` in a new Terminal tab | Shell variables are per window | Enter it again with `read -s` (section 18.8) |
| `502` or connection error on the public URL | Twenty is not running or the tunnel dropped | Check Docker and the Twenty server, then the tunnel window |
| Public URL stops working | The tunnel was restarted (the address changes) or the laptop slept | Copy the new URL from the tunnel window; keep the Mac awake |
| Twenty will not load inside an iframe | Framing is blocked by default (`X-Frame-Options`, CSP `frame-ancestors`) | Add the host's address under Settings, General, Security, Iframe embedding (section 19) |
| `PERMISSION_DENIED` ("Entity performing the request does not have permission") | The key's role does not allow that object or action | Add an object-level rule to the role (section 23) |
| `Object interaction doesn't have any "type" field` | `type` is reserved; the field is `interactionType` | Use `interactionType` (section 21.7) |
| A field or relation exists but is not listed, or "This name is already used" | Hidden field (seen with the first Assignee) | Open it by its direct address, add it as a column, or delete and recreate it (section 25) |
| A workflow does not run for a record created by hand | The screen creates the record first and fills the fields afterwards | Test with a record created through the API |
| A new role cannot be assigned to a person or key | The Applicability box was not ticked | Settings tab of the role: tick Assignable to Workspace Members or API Keys |
| An invite link opens `localhost:3000` | The copied link uses the local address | Replace the start of the link with the tunnel address (section 24) |
| Closing the lid stopped Twenty and the tunnel | The Mac slept | Start Docker and Twenty, run `pkill cloudflared`, start a new tunnel and send the new address (section 23.5) |

Other gotchas:

- A `.md` file looks messy in plain text viewers; in VS Code use Cmd+Shift+V for the preview (or Cmd+K then V for a side-by-side preview).
- Select values are uppercase with underscores in the API but show friendly labels in the UI.
- Twenty's UI and the API show the same data; refresh the browser after API changes.
- Never run `docker compose down -v` (it deletes the database volumes). Use `docker compose stop` when quitting.
- Do not write API keys, tunnel addresses or invite links into documents; the tunnel address changes at every restart.

---

## 17. What is not verified

- Whether duplicate records are prevented, and how invalid select values are rejected (not tested).
- Reading the notes attached to a record through the API (not tested).
- That a workflow can create a ticket from an incoming email (not found in documentation).
- Teams integration (only Slack was confirmed through Zapier and n8n examples).
- Round-robin or skills-based assignment as a built-in feature (none found; assumed to need a Code action).
- ~~Whether an Assignee can be a relation to a workspace member.~~ Resolved on 11 Nov: it works (section 21.4); no separate Agent object was built.
- The exact steps to create a kanban view in this version of the UI (expected from the view dropdown at the top left of the Tickets table; check what the interface offers).
- Some sample outputs in the API documentation are reconstructed (structure real, some ids and timestamps illustrative); the pending edit says so.
- Whether the iframe works with a real host on a different domain (the local test used the same site, so it did not show the cookie problem).
- ~~The exact permissions of the External API access role.~~ Resolved on 12 and 13 Nov: the role had See and Edit on all objects (her key could read opportunities). It was replaced by the **API Integration** role (section 23).
- The Cloudflare Access service-token route for API calls with a named tunnel (not verified; it also needs a domain).
- **Invite by link** was switched off on 9 Nov and switched on again on 13 Nov to send Umaima's link; it has to be turned off again (section 24).
- That **Layout All Access** and **Logic All Access** are switched off on the API Integration role (they were on by default and the instruction to turn them off was not confirmed).
- That the **SLA breach workflow for Service Requests** was built and works (steps given, test request SR-0004 not confirmed).
- That the priority alert for Service Requests reached the **Topaztel inbox** (only the test Gmail's Sent folder was checked, because Outlook was not working).
- That **Umaima's login through the tunnel** works, and which role she ended up with.
- Updating or deleting service requests, interactions and catalog entries through the API; filters on service requests other than the reference number.
- That **Interactions** has the see-only rule on the API Integration role (Tickets was tested; Interactions was not), and that her key cannot create interactions.
- That the Admin role's settings toggles are all on (the page was seen only for objects, Layout and Logic).
- Select values read back through the API: only `LOGISTICS` (team) and `ON_TRACK` (SLA status) for the Retail Tickets; `RETAIL`, `HEALTH`, `BANKING`, `REAL_ESTATE` and `GOVERNMENT` for sector. The other values follow the same uppercase pattern.

---

## 18. External access for Umaima (Cloudflare Quick Tunnel)

### 18.1 Goal and context

Umaima asked (5 Nov) whether Twenty could be reached from outside, using Cloudflare or anything free, so she could call its API. Twenty runs on Aroosh's MacBook at `http://localhost:3000`, and `localhost` only means "this computer", so she could not reach it. A **Cloudflare tunnel** gives a public HTTPS address that forwards requests to the local Twenty without deploying it anywhere, buying a domain or opening router ports. Aroosh installed `cloudflared` (`brew install cloudflared`, version 2026.10.7) and offered two options; Umaima chose option 1.

| Option | What it is | Trade-offs |
|---|---|---|
| **1. Quick tunnel** (chosen) | Free, no account or domain; a random `trycloudflare.com` address | The address changes every time the tunnel starts; meant for testing; no uptime guarantee; Cloudflare's email login gate cannot be used with API calls, so protection is a separate limited API key with an expiry, and the tunnel runs only while she tests |
| **2. Named tunnel with Cloudflare Access** | Fixed address with a proper access gate | Needs a domain added to Cloudflare (the tunnel is free; the domain is not); the Access steps for API clients were not verified |

### 18.2 Architecture

```
Umaima's computer (Postman or an external application)
        |
        v
Public Cloudflare HTTPS address (trycloudflare.com)
        |
        v
Cloudflare Quick Tunnel (outbound connection opened by cloudflared)
        |
        v
Aroosh's MacBook Air: Twenty on port 3000
        |
        v
Twenty backend and its database
```

| Component | Purpose |
|---|---|
| Twenty | The CRM being accessed |
| `localhost:3000` | Where Twenty runs locally |
| Cloudflare tunnel | Gives external access to the local application |
| API key | Authenticates Umaima's requests |
| External API access role | Defines what the key may do |
| Bearer authentication | How the key is sent in HTTP requests |

### 18.3 What "exposing" means

The tunnel makes only the one local service (Twenty on port 3000) reachable from the internet; it does not give access to the Mac, its files or its other services. The address is random but not secret, so anyone who finds it can reach Twenty's login page and API; Twenty's own login and API key are the locks. All data in this workspace is test data, which lowers the risk.

### 18.4 The dedicated role: External API access

Instead of an unrestricted Admin role, a separate role was created in Settings, Members, Roles ("+ Create Role").

**Permissions tab**

| Permission | Configuration |
|---|---|
| Delete Records on All Objects | Disabled |
| Destroy Records on All Objects | Disabled |
| Layout All Access | Disabled |
| Logic All Access | Disabled |
| Other administrative and settings permissions further down the page (workspace settings, members, roles, API keys, data model, security, workflows), where toggles were available | Disabled |

These follow the principle of least privilege: an external integration gets only what it needs.

**Settings tab (Applicability)**

| Setting | Configuration |
|---|---|
| Assignable to Workspace Members | Unchecked |
| Assignable to Agents | Unchecked |
| Assignable to API Keys | Checked |

The role is meant for API keys only, never for people or agents. A short description was added (limited access for external API testing).

**Assignment:** save the role, reopen it, open the Assignment tab, and under Assigned API keys choose "Assign to API key" and pick `Umaima external`.

**Still to verify:** the role's defaults had **See Records on All Objects** and **Edit Records on All Objects** ticked. The notes do not record narrowing them, so the key may be able to read and edit records beyond People, Companies, Tickets and Notes. To tighten it, untick See and Edit on All Objects and use "+ Add rule" (Object-Level) to allow see and edit only on People, Companies, Tickets, Notes (and Note Targets if listed). Then test that `GET /rest/opportunities` is refused and that her five operations still work.
**Update (12 to 13 Nov):** this was confirmed: the role was too broad (her key could use new objects it had never been set up for, and read `/rest/opportunities`). A new, narrow **API Integration** role was created and assigned to her key instead. See section 23.

### 18.5 The API key

| Item | Value |
|---|---|
| Name | `Umaima external` |
| Role | External API access |
| Expiry | 15 days |
| Sent as | `Authorization: Bearer <key>` |

An API key stands in for a password for software, so Umaima does not need Aroosh's login. It is a secret: never put it in public messages, repositories, screenshots or these notes. The key is shared with her separately and privately. Aroosh's own Admin key (named Retail CRM) stays private and is never shared.

### 18.6 Testing the key locally

Before opening the tunnel, the key (stored in `$UMAIMA_KEY`) was tested against `http://localhost:3000`. All five operations succeeded:

| No. | Operation | Result |
|---|---|---|
| 1 | Search an existing contact | Successful |
| 2 | Add a new contact | Successful |
| 3 | Create a ticket | Successful |
| 4 | Search tickets | Successful |
| 5 | Create a note and attach it to a ticket | Successful |

Details:

- **Search:** by email, phone and loyalty ID. The existing contact Noor Saleh was found by phone; the correct email is `noor.saleh@example.com` (an earlier try with `noor.saleh.qa@example.com` returned nothing, as expected).
- **Add contact:** `POST /rest/people` created the test contact **QA PermissionTest** (`qa.permissiontest@example.com`).
- **Create ticket:** `POST /rest/tickets` created ticket `TKT-QA-002` linked to Noor Saleh:

```json
{
  "name": "Wrong size delivered",
  "referenceNumber": "TKT-QA-002",
  "status": "OPEN",
  "priority": "HIGH",
  "category": "ORDER_ISSUE",
  "channel": "PHONE",
  "orderNumber": "ORD-QA-002",
  "description": "QA test: Customer received size M instead of L.",
  "contactId": "PERSON_ID"
}
```

- **Search tickets:** by reference number, date and date range, all returning the expected tickets.
- **Add a note** (two calls): `POST /rest/notes` with a title "Phone follow-up" and a markdown body, then `POST /rest/noteTargets` with `{"noteId": "NOTE_ID", "targetTicketId": "TICKET_ID"}`.
- The records were also checked in the Twenty UI (People, Tickets, Notes, and the note on the ticket).

**Side effect:** these test records (QA PermissionTest, TKT-QA-002, a "Phone follow-up" note) are still in the workspace, so the ticket counts in the demo script no longer match exactly.

### 18.7 Starting the tunnel
> **Update (13 Nov):** the address shown in this section's examples belongs to a tunnel that has since stopped. A new address is created at every start; see section 23.5 for what to do after the laptop sleeps.

With Twenty running on port 3000, in a second Terminal tab:

```bash
caffeinate -i cloudflared tunnel --url http://localhost:3000
```

| Part | Meaning |
|---|---|
| `caffeinate -i` | macOS utility that prevents idle sleep while the command runs |
| `cloudflared tunnel` | Starts a tunnel |
| `--url http://localhost:3000` | The local service to expose |

Cloudflare generated this public address (temporary; it changes if the tunnel is restarted):

`https://<tunnel-address>`

Cloudflare's connectivity pre-checks all passed (DNS, UDP, TCP and API connectivity in two regions), and the tunnel registered through the Dubai location (`dxb01`).

**Quick tunnel characteristics:** no account or domain needed; random address; the address stays the same only while that tunnel process runs; restarting gives a new address; no production-level uptime; it stops if the process is stopped or the laptop becomes unavailable.

### 18.8 Testing through the public address

A second Terminal tab was used, leaving the tunnel running in the first.

**Without a key**

```bash
curl -i "https://<tunnel-address>/rest/tickets?limit=1"
```

Response: `HTTP/2 403` with `{"statusCode":403,"messages":["Missing authentication token"],"error":"FORBIDDEN_EXCEPTION"}`. This is not a connection failure. It shows the public address was reachable, Cloudflare forwarded the request, Twenty received it, and Twenty rejected it for lacking a token.

**Entering the key in the new tab.** Shell variables belong to one window, so `echo ${#UMAIMA_KEY}` printed `0` in the new tab. The key was entered without displaying it:

```bash
read -s "UMAIMA_KEY?Paste Umaima's API key here: "
echo ${#UMAIMA_KEY}
```

The second command printed the key's length (greater than zero), which shows the variable is filled but not that the key is valid.

**With the key**

```bash
curl -s \
  -H "Authorization: Bearer $UMAIMA_KEY" \
  "https://<tunnel-address>/rest/tickets?limit=1" \
  | python3 -m json.tool | head -15
```

The request succeeded and returned a ticket record (the earlier test ticket). Conclusion: the public address and the key work together, and an outside request reached Twenty, was authenticated and returned data.

### 18.9 Access details for Umaima

| Item | Details |
|---|---|
| CRM | Twenty |
| Public API base URL | `https://<tunnel-address>` |
| API key name | Umaima external |
| Role | External API access |
| Key expiry | 15 days |
| Authentication | Bearer token |
| Access | REST API over HTTPS |
| Tunnel type | Cloudflare Quick Tunnel |

She does not need to log in to Twenty's web interface. In Postman: create a request, enter the endpoint, choose Authorization, Bearer Token, paste the key, pick the method, and for POST add a JSON body under Body, raw, JSON.

Endpoints (relative to the base URL):

| Operation | Method | Endpoint |
|---|---|---|
| Search contacts | GET | `/rest/people` |
| Add a contact | POST | `/rest/people` |
| Search tickets | GET | `/rest/tickets` |
| Create a ticket | POST | `/rest/tickets` |
| Create a note | POST | `/rest/notes` |
| Attach a note to a ticket | POST | `/rest/noteTargets` |

Example: `GET https://<tunnel-address>/rest/tickets?limit=1` with her key returns ticket JSON. The API documentation file (section 11) has the full request and response samples; she replaces `http://localhost:3000` with the public address.

### 18.10 What must stay running

- **Terminal tab 1:** Twenty (Docker) running at `http://localhost:3000`. If it stops, the tunnel has nothing to forward to.
- **Terminal tab 2:** the `cloudflared` tunnel. If it stops, the public address stops working.
- Keep both open, do not press Ctrl+C in either during testing, keep the Mac awake and online, and do not restart the tunnel unless ready to send her the new address. `caffeinate -i` helps prevent idle sleep but does not guarantee connectivity.
- Her key and the tunnel are separate from Aroosh's own work: Aroosh can keep using Twenty locally. Records Umaima's key creates or changes appear in Aroosh's Twenty.

### 18.11 Security considerations

- **No access to the Mac.** The tunnel forwards web requests to port 3000 only. It gives no remote desktop, files, Terminal, browser history or other local services.
- **The web interface is also reachable.** The tunnel exposes the whole Twenty service on port 3000, so the login page is reachable too. Use a strong password and switch off **Invite by Link** (Settings, General, Security), which lets anyone with the link join the workspace.
- **The key does not log her into the web interface**, but access to the API and to the web interface are separate questions.
- **The role does not guarantee only five operations.** The five were tested, but that does not prove everything else is blocked. The See and Edit permissions need reviewing (18.4).
- Share the key only through a private channel; never in a group chat or a document.
- Run the tunnel only while she tests; stop it with Ctrl+C in its window.
- Revoke the key when no longer needed instead of waiting for the 15-day expiry.

### 18.12 Message sent to Umaima

> Hi Umaima, the Cloudflare Quick Tunnel is set up, and I've successfully tested the public Twenty API URL using the API key.
> API Base URL: https://<tunnel-address>
> I'll share the API key separately.
> The key has the configured role permissions and a 15-day expiry. The tunnel is temporary, so I'll keep it running while you're testing. Please note that the URL will change if I restart the tunnel.
> Let me know if you run into any issues accessing the API.

### 18.13 Status

**Done:** Twenty running locally; External API access role created (delete, destroy, layout, logic and other admin toggles disabled; assignable only to API keys); role assigned to `Umaima external`; 15-day expiry; the five operations tested locally; Cloudflare tunnel started with a public HTTPS address; connectivity pre-checks passed; unauthenticated request rejected with 403; key entered in the new Terminal tab; authenticated public request returned ticket data; both Terminal tabs still running.

**Remaining:** Umaima tests from her own computer and confirms the five operations; review object-level permissions; confirm whether she needs any extra permission; stop the tunnel and revoke the key after testing.

**Summary:** a dedicated limited role and key were created and tested locally, and a temporary Cloudflare Quick Tunnel now lets Umaima call the Twenty REST API from her own computer, with no public deployment and no purchased domain, as long as Twenty and the tunnel keep running on the MacBook.

---

## 19. Iframe embedding (screen pop)

### 19.1 The request

Umaima asked to check how to allow someone to embed Twenty in an iframe as a **screen pop** (when a call arrives, the agent's screen shows the caller's record), noting that by default it will not allow it. After Aroosh explained how a call could lead to a record (the API finds the contact by phone number and returns the record id, from which the record's address is built), Umaima said that is how INVOQ does it, and asked to see whether Twenty has an option to **whitelist a host** for iframing, since some CRMs do.

### 19.2 Why it is blocked by default

Browsers refuse to show a page in an iframe if the page says so with the `X-Frame-Options` header or the `frame-ancestors` part of the `Content-Security-Policy` header. Checked on this instance:

```bash
curl -s -I http://localhost:3000 | grep -i -E "x-frame-options|content-security-policy"
```

```
X-Frame-Options: SAMEORIGIN
Content-Security-Policy: frame-ancestors 'self'; object-src 'none'; base-uri 'self'; manifest-src 'self'
```

A test page on another origin showed Chrome blocking it: "Framing 'http://localhost:3000/' violates the following Content Security Policy directive: frame-ancestors 'self'. The request has been blocked."

### 19.3 What was found

Twenty's documentation says nothing about embedding, and no environment variable for it was set in the container. The server code (`frontend.service.js` in the container) reads a per-workspace list called `allowedIframeOrigins`. When the list is not empty, it sets `frame-ancestors 'self'` plus those origins and removes `X-Frame-Options`, keeping the other CSP rules.

The setting is in the UI: **Settings, General, Security, Iframe embedding** ("Websites allowed to embed this workspace. Only add ones you fully trust."), with an **Allowed origin** field and **Add origin**. An origin is the scheme, host and port only, with no path (for example `https://agent.example.com`).

(A reverse proxy that rewrites the headers was also drafted as a fallback, but it was not needed and not run.)

### 19.4 Test that was run

1. A test page served locally: `mkdir -p ~/iframe-test && cd ~/iframe-test`, a `test.html` containing `<iframe src="http://localhost:3000" width="1000" height="700"></iframe>`, and `python3 -m http.server 8080`. Before the setting, the frame was blank and the console showed the CSP message above.
2. `http://localhost:8080` was added as an allowed origin.
3. The header check then showed no `X-Frame-Options` and `Content-Security-Policy: frame-ancestors 'self' http://localhost:8080; object-src 'none'; base-uri 'self'; manifest-src 'self'`.
4. Reloading the test page showed Twenty inside the frame, logged in (the Companies table).

**Limit of the test:** `localhost:8080` and `localhost:3000` count as the same site, so it did not show the cookie problem. With a host on a different domain, browsers may block cookies inside the frame and the agent may see the login screen. It works best when the host and Twenty share a parent domain, and it should be tested with the real addresses.

### 19.5 Clean-up and the real setup

1. Remove `http://localhost:8080` from Iframe embedding.
2. Stop the test server with Ctrl+C in its window.
3. Recheck the header; `X-Frame-Options: SAMEORIGIN` should be back:

```bash
curl -s -I http://localhost:3000 | grep -i -E "x-frame-options|content-security-policy"
```

4. For the real use, add the address of the INVOQ agent screen as the allowed origin.
5. A simpler alternative that avoids the cookie and URL problems is opening the contact in a new browser tab or window instead of an iframe.

### 19.6 Message sent and what is pending

Aroosh told Umaima that Twenty is blocked by default, why, the two things that can still break it (the login cookie issue, and building the record address from the phone lookup), and the new-tab alternative. After finding the setting, the update to send is: the whitelist exists (Settings, General, Security, Iframe embedding), it was tested locally, and the only thing needed is the address of the INVOQ agent screen (scheme, host and port) and whether it shares a domain with Twenty. That reply was still to be sent when this was written.

---

## 20. References

Twenty documentation:

- Workflows overview: https://docs.twenty.com/getting-started/core-concepts/workflows
- Workflow actions: https://docs.twenty.com/user-guide/workflows/capabilities/workflow-actions
- Workflow triggers: https://docs.twenty.com/user-guide/workflows/capabilities/workflow-triggers
- Send emails from workflows: https://docs.twenty.com/user-guide/workflows/capabilities/send-emails-from-workflows
- Workflow credits: https://docs.twenty.com/user-guide/workflows/capabilities/workflow-credits
- Calendar and email: https://docs.twenty.com/user-guide/calendar-emails/overview
- Roles and permissions: https://docs.twenty.com/user-guide/permissions-access/capabilities/permissions
- Permissions FAQ: https://docs.twenty.com/user-guide/permissions-access/how-tos/permissions-faq
- Apps and workflows for developers: https://docs.twenty.com/developers/extend/apps/logic/workflows
- Self-hosting with Docker Compose: https://docs.twenty.com/developers/self-host/capabilities/docker-compose

Integrations:

- Slack and Twenty on Zapier: https://zapier.com/apps/slack/integrations/twenty/255631178/send-direct-messages-in-slack-when-new-record-triggers-occur-in-twenty

Comparison material:

- Freshdesk SLA policies: https://support.freshdesk.com/en/support/solutions/articles/37626
- Freshdesk escalation emails: https://support.freshdesk.com/en/support/solutions/articles/228175-how-to-send-escalation-emails-to-unresponsive-agents-
- Salesforce Service Cloud overview: https://www.salesforcetutorial.com/service-cloud/
- Sales Cloud versus Service Cloud: https://salesforceben.com/sales-cloud-vs-service-cloud/

External access and tunnels:

- Cloudflare quick tunnels: https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
- Cloudflare Tunnel, remotely managed tunnels: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/index.md

---

## 21. INVOQ build on the Retail Tickets (9 to 11 November)

This is the build order from section 15.2, done in the Twenty UI and tested through the API. Nothing here contains a key. Where a key or address is needed, a placeholder is used.

### 21.1 Overview

| Build step | What was built | Status |
|---|---|---|
| 1. Test mailbox and priority email | A dedicated test Gmail account connected to Twenty; workflow **High priority ticket email** | Done and tested |
| 2. Assignee, Team and roles | Assignee relation to a workspace member, Team select; roles Agent, Supervisor and Admin | Done; the Agent role was tested with a second user |
| 3. SLA fields and escalation | First Response Due, Resolution Due, SLA Status; workflow **SLA breach escalation** every 15 minutes | Done, tested and active |
| 4. Interaction history | An **Interaction** object linked to tickets, contacts and agents; 8 sample interactions | Done |
| 4b. Agent object | Not built. Workspace members are used as agents instead (the Assignee and Handled By relations) | Decision made |
| 5. Read-only API key | Not built as such; replaced by the limited **API Integration** role (section 23) | Superseded |
| 6. Comparison write-up (Twenty, Salesforce, Freshdesk) and design summary | Research exists (section 13); no separate write-up | Open |
| 7. Workflow that creates a ticket from an incoming email; Teams message by HTTP request | Not tested | Open |

### 21.2 Test mailbox and email sending (9 Nov)

- A separate Gmail account was created for testing, with 2-Step Verification turned on and an **app password** created (Google Account, Security, App passwords). The app password is a secret like an API key: never write it in a document.
- This self-hosted Twenty offered only **Connect via IMAP/SMTP** under Settings, Accounts (no "connect with Google" button). Form values: IMAP server `imap.gmail.com`, port 993, SSL/TLS; SMTP server `smtp.gmail.com`; username the full address; password the app password; CalDAV left blank.
- The first save failed with "couldn't connect to your SMTP server". Ports 587 and 465 were reachable from the Mac (`nc -vz`) and from inside the server container, so the network was fine. It saved after setting the SMTP port to **465 with SSL/TLS**. The account then showed **Synced**.
- Suggested at the time: set **Contact auto-creation** to None under Settings, Accounts, Emails, so sent emails do not create People records.
- Twenty sending an email can be proved from the test Gmail's **Sent** folder, independent of whether the receiving inbox is working (on 13 Nov Outlook was not receiving, and this was how the emails were confirmed).

### 21.3 Workflow: High priority ticket email (9 Nov)

| Part | Setting |
|---|---|
| Trigger | **Record is created** on **Tickets**. In this version the condition sits inside the trigger: Priority is High and Urgent (no separate Filter step) |
| Action | **Send Email**: From the test Gmail account; To a Topaztel address; Subject `High priority ticket: ` + the Reference Number; Body `A high priority ticket was created: ` + Name + ` - ` + Reference Number |

How to build it: Workflows, New Workflow, trigger, then **+** for the action. Insert values with the **(x)** variable picker, never by typing `{{ }}`. Spaces next to a chip have to be typed (the first email had none).

Tests:

- A ticket created **through the API** with priority HIGH (TKT-0014) and URGENT (TKT-0016) sent an email each; the LOW ticket (TKT-0015) sent nothing and produced no run.
- Tickets created **by hand in the UI** (TKT-0013 and TKT-0007) produced no run. The UI creates the record first and fills the fields afterwards, so the priority was still empty when "Record is created" fired. Tickets created through the API arrive with every field set, which is how INVOQ would create them.
- Possible improvement not done: show the actual priority in the subject, so an Urgent ticket does not say "High priority".

### 21.4 Assignee and Team (9 to 11 Nov)

- **Team:** select field with Support, Billing, Logistics and Escalations (API values are uppercase, for example `LOGISTICS`).
- **Assignee, first attempt (9 Nov):** created from + New Field, which opened a relation screen whose URL ends in `MORPH_RELATION` and whose destination defaulted to Company. The field was saved with **two destinations** (Companies and Workspace Members). Symptoms: the Data model page did not list it, creating it again said "This name is already used", it worked as a column in the Tickets table, and the API showed two columns (`assigneeCompanyId` and `assigneeWorkspaceMemberId`), so a company could be picked as an assignee.
- **Fix (11 Nov):** open `localhost:3000/settings/objects/tickets/assignee` directly (Relation type and Object destination are greyed out, so they cannot be edited), **Delete** the field, then create it again: Belongs to one, destination **Workspace Member** only, field on destination `Assigned tickets`. The API field is now `assigneeId`. Checked by setting an assignee on TKT-0007 and reading it back.

### 21.5 Roles: Agent, Supervisor, Admin (9 Nov)

Created in Settings, Members, Roles (+ Create Role). Every role needs **Assignable to Workspace Members** ticked on its Settings tab, otherwise it cannot be assigned to a person (the Assignment tab's "+ Assign to member" stays disabled).

| Role | Objects | Layout and Logic | Settings permissions |
|---|---|---|---|
| Agent | See and Edit on All Objects; no Delete or Destroy | Off | All off (Developers, Workspace, Users, Roles, Data Model, Security, Workflows and the rest) |
| Supervisor | See, Edit and Delete on All Objects; no Destroy | Off | All off |
| Admin | See, Edit, Delete and Destroy | On | Meant to be all on |

Findings and test:

- The Roles list showed only Member at first and later Agent, Member and Supervisor, but not Admin. Admin did exist (it appears in the Invite role dropdown), and creating it again says "A role with this label already exists". The list under-reports roles; the Invite dropdown shows them all.
- A test member was invited with the test Gmail account (invite link opened in that account's Chrome profile). The invite used the default role (Member), and **Test Agent** was moved to Agent from Settings, Members, the member's page, Permissions tab, Role dropdown, then Update role. The role's own Assignment tab said "All workspace members already have this role" and kept its button disabled.
- Agent check: Settings showed only the User section (Profile, Experience, Accounts, Documentation, Logout), and ticket edits worked. Supervisor and Admin both showed the Delete option, as configured. The test member was set back to Agent.

### 21.6 SLA fields and workflow: SLA breach escalation (10 Nov)

Fields on Tickets: `firstResponseDue` and `resolutionDue` (date and time), and `slaStatus` (select On Track, At Risk, Breached).

| Step | Setting |
|---|---|
| Trigger | **On a schedule**, every 15 minutes (the default is once a day at 00:05 UTC, so the interval has to be changed; times are UTC) |
| Search Records (Tickets) | Resolution Due **is in past**, and SLA Status is On Track or At Risk, and Status is Open or In Progress; limit 50 |
| Iterator | Over **All Tickets** from the search (actions go on the **loop** branch) |
| Update Record | Tickets, the iterator's current item **ID**, SLA Status set to **Breached** |
| Send Email | From the test Gmail; To a Topaztel address; Subject `SLA breached: ` + Reference Number; Body `Ticket ` + Reference Number + ` - ` + Name + ` has passed its resolution deadline.` |

Lessons: use the **Is in past** operator, because **Is before** with a typed date is fixed at the moment it was typed; the SLA Status condition is what stops the same ticket being emailed every 15 minutes; chips must come from the iterator's **Current Item**, not from Search Records (**First Ticket** is always the first record). The first test email repeated the ticket name because a stray Name chip was left at the start of the body.

Tests: TKT-0020 was created through the API with a resolution date of 1 Nov, priority MEDIUM (so the priority email did not fire) and SLA Status On Track. Clicking **Test** completed every step, the ticket changed to **Breached** and the email arrived. The workflow was activated; runs #2 and #3 on the schedule completed with nothing to process and no repeat email.

### 21.7 Interaction object (11 Nov)

Created in Settings, Data model, + New object: singular Interaction, plural Interactions. API endpoint `/rest/interactions`.

| Field | Type | Notes |
|---|---|---|
| Name | Text | Record label; the script names records like `Wrong size call` |
| Type | Select | Call, Email, Chat, SMS. **API field `interactionType`** (see below) |
| Direction | Select | `INBOUND`, `OUTBOUND` |
| Occurred At | Date and time | UTC |
| Duration Seconds | Number | Calls only |
| Summary | Text | |
| Outcome | Select | `RESOLVED`, `FOLLOW_UP_NEEDED`, `ESCALATED` |
| Ticket | Relation (belongs to one) | API `ticketId`; the ticket shows an Interactions list |
| Contact | Relation (belongs to one) | API `contactId`; left empty on the sample data |
| Handled By | Relation to Workspace Member | API `handledById` |

Quirks:

- Twenty reserves the name `type`, so the Type field was saved with the API name `typeCustom` (an API call with `type` returned `Object interaction doesn't have any "type" field`). On 11 Nov the API name was changed to `interactionType`: open the field, switch **Synchronize Field Label and API Name** off, type the API name in the new API Name box, Save. The label stays Type. This only works for the API name; the select values were not affected.
- A relation column shows the related record's **label** (the ticket Name, not its reference number). To show the reference number, either change the ticket's label identifier (affects every place tickets appear) or put the reference in the interaction name. Neither has been done.
- Select values and relation names are visible in the UI, but only a record read back through the API shows the true field names.

### 21.8 Sample interactions (11 Nov)

Eight interactions were created through the API and linked to TKT-0001 to TKT-0006 (Handled By set to Aroosh): a call about the damaged item (310 s), a refund email and a refund call (180 s), a delivery tracking chat, a wrong size call (420 s) and its exchange confirmation email, a missing item email, and a late delivery call (260 s). They were checked in the Interactions table, and TKT-0004's page lists its two interactions. One manual record, **Test call**, is tied to the test ticket TKT-0030 ("Test Ticket to check Interactions working"). The optional step of copying each ticket's contact onto its interactions and putting reference numbers into interaction names has not been done.

### 21.9 Test records added to the workspace

| Record | What it is |
|---|---|
| TKT-0013 "Workflow email test" | Created by hand to test the workflow; assignee Aroosh; priority cleared |
| **TKT-0007 "Workflow email test 2"** | Created by hand; now In Progress, Medium, Team Logistics, assignee Aroosh. **The live-demo script in section 9 also uses TKT-0007**, so the reference number is already taken |
| TKT-0014, TKT-0015, TKT-0016 | API-created tests for the High, Low and Urgent email workflow |
| TKT-0020 "SLA breach test" | API-created; now Breached |
| TKT-0030 "Test Ticket to check Interactions working" | Linked to the manual Test call interaction |
| QA PermissionTest, TKT-QA-002, a "Phone follow-up" note | Earlier, created with Umaima's key (section 18.6) |

All of these were deliberately kept (not deleted). The ticket count is now about 20, so the counts in the demo script (section 9.4, "7 tickets") no longer match; check a count before quoting it.

---

## 22. Generic Service Request module (11 to 13 November)

### 22.1 The request (11 Nov)

Umaima asked for a **generic ticketing module** so that INVOQ, acting as a screen pop that serves several industries, does not need industry-specific fields: a basic Ticket / Service Request with **one field that accepts the Sector or Industry (Retail, Health, Real Estate, Banking, Government)** and generic fields such as **Category** and **SubCategory**. It had to be created as a **new module** so the existing Tickets module is left unchanged, and she asked for **the changes in the API payload for Create ticket**.

Aroosh asked whether Category and SubCategory should be free text or fixed lists per sector. Umaima answered: free text, and **dependent lists based on the sector** if possible.

### 22.2 Design decisions

- The object is called **Service Request** (the name Ticket was taken). Endpoint `/rest/serviceRequests`.
- Category and Sub Category are **free text**, so no industry-specific lists live in the module.
- Twenty has **no dependent dropdowns** (one select cannot change its options based on another field). The solution is a small second object, the **Catalog Entry**, which stores valid Sector / Category / SubCategory combinations. INVOQ reads it through the API to build the dependent dropdowns, and saves the chosen values as text. Twenty does not reject a category that is not in the catalog.
- Not carried over: Order Number (retail specific), the Retail category list, and the Team field (its options are retail-like).
- An optional **External Reference** field holds the INVOQ interaction or screen-pop id.

### 22.3 Service Request fields

| Field (API name) | Type | Values / notes |
|---|---|---|
| Name (`name`) | Text | Subject |
| Reference Number (`referenceNumber`) | Text | For example `SR-0001`; supplied by the caller |
| Sector (`sector`) | Select | `RETAIL`, `HEALTH`, `REAL_ESTATE`, `BANKING`, `GOVERNMENT` |
| Category (`category`) | Text | Free text |
| Sub Category (`subCategory`) | Text | Free text |
| Description (`description`) | Text | |
| Status (`status`) | Select | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` |
| Priority (`priority`) | Select | `LOW`, `MEDIUM`, `HIGH`, `URGENT` |
| Channel (`channel`) | Select | Phone, Email, Chat, SMS, Web, In person (`PHONE` and `EMAIL` verified) |
| External Reference (`externalReference`) | Text | Optional |
| Contact (`contactId`) | Relation to People | Belongs to one; the person has a Service Requests list |
| Account (`accountId`) | Relation to Companies | Belongs to one |
| Assignee (`assigneeId`) | Relation to Workspace Member | Belongs to one; the field on the member is "Assigned service requests" |
| First Response Due (`firstResponseDue`), Resolution Due (`resolutionDue`) | Date and time | Added 13 Nov |
| SLA Status (`slaStatus`) | Select | On Track, At Risk, Breached (added 13 Nov) |

The API names were confirmed by reading back a record created by hand ("testing record 1", sector Health, kept in the workspace).

### 22.4 Category Catalog (dependent lists)

Object **Catalog Entry** (plural Catalog Entries, endpoint `/rest/catalogEntries`) with fields Name (a label such as `BANKING / Cards / Card blocked`), Sector (the same five options), Category and Sub Category. 20 sample entries were loaded through the API:

| Sector | Category | Sub categories |
|---|---|---|
| Retail | Order issue | Wrong item, Late delivery |
| Retail | Returns and refunds | Refund status, Return request |
| Health | Appointments | Book or reschedule, Cancellation |
| Health | Billing | Invoice query, Insurance claim |
| Real Estate | Property enquiry | Viewing request, Pricing |
| Real Estate | Maintenance | Repair request, Urgent issue |
| Banking | Cards | Card blocked, Lost or stolen |
| Banking | Account access | Password reset, Locked account |
| Government | Applications | Status check, Missing documents |
| Government | Complaints | Service delay, Staff conduct |

How INVOQ uses it:

1. When the agent picks a sector, call `GET /rest/catalogEntries?filter=sector[eq]:BANKING&limit=200` and take the distinct `category` values for the first dropdown. (Verified result for Banking: Account access, Cards.)
2. When a category is picked, filter the same rows by `category` on the INVOQ side for the second dropdown. (Verified for Account access: Locked account, Password reset.)
3. Create the request with `POST /rest/serviceRequests`, sending the chosen values as text.

### 22.5 Payload changes (Retail Tickets versus Service Requests)

| | Retail Tickets | Service Requests |
|---|---|---|
| Create endpoint | `POST /rest/tickets` | `POST /rest/serviceRequests` |
| Industry | Not present | `sector`: `RETAIL`, `HEALTH`, `REAL_ESTATE`, `BANKING`, `GOVERNMENT` |
| `category` | Select (`ORDER_ISSUE`, `DELIVERY` and so on) | Free text |
| `subCategory` | Not present | Free text |
| `orderNumber` | Present (retail specific) | Removed |
| `channel` | Includes `STORE` | Generic list (Phone, Email, Chat, SMS, Web, In person) |
| `externalReference` | Not present | Optional, the INVOQ interaction id |
| Everything else | `name`, `referenceNumber`, `description`, `status`, `priority`, `contactId`, `accountId`, `assigneeId` | The same |

Example payload (tested):

```json
{
  "name": "Customer cannot access account",
  "referenceNumber": "SR-0001",
  "sector": "BANKING",
  "category": "Account access",
  "subCategory": "Password reset",
  "description": "Caller locked out after three attempts.",
  "status": "OPEN",
  "priority": "HIGH",
  "channel": "PHONE",
  "assigneeId": "<WORKSPACE_MEMBER_ID>",
  "externalReference": "INVOQ-INT-48213"
}
```

### 22.6 Records and tests (12 to 13 Nov)

- Catalog loaded with a script (20 entries); the two dependent-list queries above returned the expected values.
- **SR-0001** (Banking) created through the API and read back by reference number. **SR-0002** (Retail, "Wrong item delivered") created with a contact (Noor Saleh), an account (Urban Wear Boutique), an assignee and an external reference; all links were saved and displayed in the UI.
- Umaima's key was tested for the new objects (section 23); the test requests it created (`Key test`, `Key test 2`, references `SR-TEST` and `SR-TEST2`) are to be deleted.

### 22.7 Applying the Retail features to Service Requests (13 Nov)

After the module was sent, Aroosh asked Umaima whether she wanted anything else on the generic modules (a short message listing what the Retail Tickets now have). Umaima answered **"yea you can apply"**.

| Feature | Status |
|---|---|
| SLA fields | Done: `firstResponseDue`, `resolutionDue`, `slaStatus` exist on Service Requests (checked by reading a record) |
| Interaction history | Done: Interaction has a new **Service Request** relation (`serviceRequestId`); three sample interactions (a call and an email for SR-0001, a chat for SR-0002) were loaded and checked on the request pages |
| Priority alert email | Done and tested: workflow **High priority service request email** was a duplicate of the Tickets one, with the record type switched to Service Requests. SR-0003 (Urgent, Banking) was created; the run completed and the email shows in the test Gmail's Sent folder (subject `Service request URGENT - SR-0003`). Delivery to the Topaztel inbox was not checked because Outlook was not working that day |
| SLA breach workflow | Steps were given (duplicate **SLA breach escalation**, switch the search to Service Requests, rebuild the iterator input, update step and email chips); **not confirmed built or tested**. A test request `SR-0004` with a past resolution date was planned |
| Roles | Agent, Supervisor and Admin have rules on All Objects, so they cover Service Requests automatically (not tested separately) |
| Interactions through the API | Umaima's key can only read Interactions; letting INVOQ create them needs an edit rule on that object (asked, not answered) |

### 22.8 Messages sent to Umaima about the module

- **Module message (13 Nov):** the Create endpoint and fields, the sector values, the catalog endpoint for dependent lists, the payload changes, what her key can do, the key expiry, and a question about copying the automations. The key was sent separately.
- **Tunnel address change (13 Nov):** when the laptop was closed the tunnel stopped and a new address was created; she was sent the new address (section 23.5).
- **Add-on (13 Nov):** a short summary of the Retail Tickets features (Assignee and Team, SLA fields and breach alert, High and Urgent alert email, roles, interaction history) and the question about the generic modules, which she answered with "yea you can apply".

---

## 23. API access update: the API Integration role (12 to 13 November)

### 23.1 What was found

On 12 Nov Umaima's key was used with the new objects, and creating a service request worked. That was a warning: the **External API access** role (section 18.4) had been created before those objects existed, yet the key could use them, which shows it still had **See and Edit on All Objects**. A key with that role could also read other objects: on 13 Nov a read of `/rest/opportunities` with her key returned data. That role is hidden from the Roles list in the UI (it is only visible as the role on the key under Settings, Developers, API keys), so it could not be edited from the Roles page.

### 23.2 The new role

A clean role was created: Settings, Members, Roles, + Create Role, named **API Integration** (description "Limited access for the INVOQ integration").

| Setting | Configuration |
|---|---|
| Settings tab: Applicability | **Assignable to API Keys** ticked; Workspace Members and Agents unticked |
| All Objects | See, Edit, Delete and Destroy all unticked |
| Object-level rules | Catalog Entries: see; Companies: see and edit; People: see and edit; Service Requests: see and edit; Tickets: see only; Interactions: see only |
| Layout All Access, Logic All Access | Should be off (they were on by default; to be confirmed switched off) |
| Settings permissions | Off |
| Workspace Members | Not offered as an object rule; creating a request with an `assigneeId` still worked |

Umaima's wish was that the key could see the related objects (such as Tickets) but nothing more, so Tickets and Interactions were added as **see-only object rules** instead of ticking See Records on All Objects.

The role was assigned to the key from Settings, Developers, API keys, **Umaima external**, Role dropdown (changing the dropdown took effect; the role's Assignment tab did not list the key before that). **Regenerate Key** must not be used for this: it invalidates the key she already has.

### 23.3 Tests (all with her key)

| Call | Result |
|---|---|
| Read catalog entries | Returned data |
| Create a service request with an `assigneeId` | Created |
| Read tickets | Returned data |
| Create a ticket | `PERMISSION_DENIED` (HTTP 400, "Entity performing the request does not have permission") |
| Read opportunities | `PERMISSION_DENIED` |

The first attempt to move the key onto the new role did not take effect (opportunities still returned data); it worked once the key's own Role dropdown was set to API Integration.

### 23.4 Key

| Item | Value |
|---|---|
| Name | `Umaima external` |
| Role | API Integration (was External API access) |
| Expiry | Created 6 Nov with 15 days; the key page showed "Expires in 7 days" on 13 Nov, so about **20 Nov** |

If she needs the API after that, create a new key (Settings, Developers, API keys, + Create API key) under the API Integration role with a 30-day expiry, and send it privately. Her key was tested through the public address as well as locally.

### 23.5 The tunnel: restarts and new addresses

The Cloudflare Quick Tunnel address changes **every time the tunnel starts**. On 13 Nov a first tunnel address was created and tested (a 403 without a key proves the tunnel works, because it reached Twenty; with her key the catalog returned data). When the MacBook lid was closed the Mac slept, which stopped Docker and the tunnel, and the same command created a **new** tunnel with a new address; the old address cannot be revived. The new address was tested the same way and sent to Umaima. Rules learned:

- Closing the lid sleeps the Mac even with `caffeinate -i`; keep the lid open and the Mac plugged in while she tests.
- After a sleep: check `localhost:3000` loads (otherwise `open -a Docker`, then `cd ~/twenty && docker compose up -d`), run `pkill cloudflared` to clear leftovers, start one tunnel, copy the address from the "Your quick Tunnel has been created" box, test it, and tell her.
- Stop Twenty with `docker compose stop`, not `docker compose down -v` (the `-v` deletes the database volumes and everything built).
- Tunnel addresses and keys are deliberately not written in this file.
- A permanent address would need a named Cloudflare tunnel, which needs a free Cloudflare account (not set up).

---

## 24. Umaima's login to the CRM (13 Nov)

Umaima asked for a login to the Twenty web interface. A **Supervisor** invitation was created for her work email (Settings, Members, Invite, role Supervisor; it is listed as pending and expires in 30 days). The link that was sent to her, with the tunnel address in place of `localhost:3000`, is the **workspace-wide Invite by link**, not her personal invitation.

Things to check and finish:

1. **Role.** The workspace link gives whoever uses it the workspace's default role (Member), not necessarily Supervisor. After she signs up, open Settings, Members, Team, find her, and set the role to Supervisor (Admin only if she wants to see the data model and workflows).
2. **Invite by link is on.** It was switched off on 9 Nov but had to be on to copy the link. Anyone who gets the link can join. Turn it off (Settings, General, Security) once she has signed up, which also invalidates the link.
3. **Login through the tunnel was not verified.** Signing in through the public address was planned to be tested in a private window with the Test Agent account, but the result was not reported. If the login page loads but hangs, offer her a screen-share instead.
4. Her login only works while the Mac is awake, Docker is up and the tunnel is running; a new tunnel address needs a new link.
5. Remove her from Members, Team when review is finished, or leave her in for later reviews.

---

## 25. Twenty UI quirks and lessons from the build

| Quirk | What to do |
|---|---|
| Some fields and relations exist but are not listed under Settings, Data model (the first Assignee) | Open the field by its direct address (`/settings/objects/<object>/<field>`) or add it as a column from the table's display options |
| A new field says "This name is already used" although it is not listed | The field exists (hidden). Use it, delete it from its direct address, or choose another name |
| Relation fields open a screen whose URL ends in `MORPH_RELATION`, and the destination can default to Company | Set **Belongs to one** and a single destination every time; the box must not say "2 Objects". Destination cannot be edited later |
| The Roles list hides some roles (Admin, External API access) | Use the Invite dropdown or the key's Role dropdown to see all roles |
| A role's Assignment tab button is disabled ("All workspace members already have this role") | Change the role from the member's page, or the key's page |
| A new role cannot be assigned to people | Tick **Assignable to Workspace Members** (or API Keys) on the Settings tab |
| Twenty reserves the field name `type` | The API name becomes `typeCustom`; rename it with **Synchronize Field Label and API Name** off |
| A relation column shows the related record's Name, not its reference number | Change the label identifier, or put the reference in the name |
| The Retail ticket demo script uses TKT-0007 | That reference is taken by a test ticket (section 21.9) |
| Workflows with "Record is created" do not fire for records created by hand with empty fields | Test them with API-created records |
| New workflows do not run until **Activate**; the Test button runs the steps once | Use Test first, then Activate |
| Duplicating a workflow keeps the old object's variables | Switch the record type, then delete and re-pick every chip with the (x) picker |
| Workflow run lists include failed runs of the built-in "Create company when adding a new person" workflow | Unrelated; ignore |
| Closing the lid kills Docker and the tunnel | Keep the lid open and plugged in while someone tests |
