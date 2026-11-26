# Deploying the CRM on a new server

This guide sets up the CRM on **any** Ubuntu server: Google Cloud, another cloud, or a Topaz internal server.
It is exactly how the live copy at https://crm.34-18-187-167.sslip.io was built on 19 November 2026.

There are two ways to fill the CRM with data. Steps 1 to 3 are the same for both.

| | **Way A: with the export file** | **Way B: from Aroosh's documents** |
|---|---|---|
| Result | An **exact copy** of Aroosh's CRM: every record, her users, passwords and API keys | The same structure and the sample records written in her documents; new users and keys |
| Needs | The file `data/twenty-export-<date>.enc` and its passphrase | An Admin account and an API key on the new CRM |
| Time | About 10 minutes | About 15 minutes |
| Used for the live copy? | **Yes** (since 19 Nov 2026) | Earlier the same day, then replaced by Way A |

---

## Step 1. The server you need

- **Ubuntu 24.04** (or 22.04). Debian 12 also works.
- At least **2 processors, 4 GB memory, 30 GB disk**. (The live copy: Google Cloud e2-medium, 40 GB disk.)
- **Ports 80 and 443** reachable from the users' computers (for HTTPS), and **SSH** for the administrator.
- **A name for the server:**
  - with a company domain: create a DNS "A record", for example `crm.yourcompany.com` → the server's IP address;
  - without a domain, on a public IP: use `crm.<ip-with-dashes>.sslip.io` (example: IP 34.18.187.167 →
    `crm.34-18-187-167.sslip.io`). Nothing to set up; it works by itself.
  - On an **internal-only** server (no public IP), the automatic certificate cannot be issued; see
    [docs/OPERATIONS.md](docs/OPERATIONS.md), "Internal servers without internet access".

On Google Cloud, the live server was created like this (project and zone are ours; change them for yours):

```bash
gcloud compute instances create aroosh-crm --zone=me-central1-a --machine-type=e2-medium \
  --image-family=ubuntu-2404-lts-amd64 --image-project=ubuntu-os-cloud \
  --boot-disk-size=40GB --boot-disk-type=pd-balanced --tags=twenty-web
gcloud compute addresses create aroosh-crm-ip --addresses=<the external IP shown> --region=me-central1
```

The first command makes the server; the second keeps its IP address fixed, so the web address never changes.
The tag `twenty-web` matches a firewall rule that opens ports 80 and 443.

## Step 2. Put this repository on the server

The repository is **public**, so no GitHub login is needed:

```bash
sudo apt-get install -y git
git clone https://github.com/rishitopaz/twenty-crm-invoq-deploy.git
```

No internet on the server? On your own computer open the repository page → green **Code** button → **Download ZIP**,
copy the ZIP to the server (`scp`), and unzip it.

## Step 3. Prepare the server (once, about 2 minutes)

```bash
cd twenty-crm-invoq-deploy
sudo bash scripts/setup-ubuntu.sh
```

This installs Docker (from Docker's official source), turns on the firewall (only SSH, 80 and 443 are allowed),
switches on automatic security updates, and adds 2 GB of swap on small machines.
**Log out and log back in once** afterwards, so your user may run Docker.

---

## Step 4A. Way A: deploy Aroosh's exact data (about 10 minutes)

You need the export file in `data/` and its passphrase. For `data/twenty-export-20261120-1412.enc` only **Rishi** has
the passphrase; ask him by phone. It is never written down in GitHub.

```bash
cd twenty-crm-invoq-deploy
scripts/import-export.sh data/twenty-export-<date>.enc
```

With your own domain, add it at the end: `scripts/import-export.sh data/twenty-export-<date>.enc crm.yourcompany.com`

The script asks for the passphrase and then does everything by itself:

1. opens the file and creates the settings file `.env`, with the **same secret keys** as Aroosh's laptop
   (so her logins, passwords and API keys keep working) and the **same Twenty version**;
2. starts the database and loads all the data;
3. starts Twenty and HTTPS, and puts back uploaded files (attachments, pictures);
4. counts the rows in every table and compares them with the laptop. **`DATA IDENTICAL`** means it is an exact copy;
5. deletes the unencrypted working copy.

The last line shows the address: `LIVE: https://...`. Log in with the same email and password as on Aroosh's CRM.

**Then upgrade to the current version.** The file was made on 20 Nov 2026, when the CRM ran **v2.51.0**, so the import
starts v2.51.0. The live CRM runs **v2.59.3**. Upgrade the same way the live one was upgraded on 26 Nov 2026:
[docs/OPERATIONS.md](docs/OPERATIONS.md), section 4 (backup, snapshot, change `TAG` to `v2.59.3`, restart, check). About
5 minutes.

## Step 4B. Way B: build from Aroosh's documents (about 15 minutes)

**4B.1 Create the settings file.** Copy the template and fill it in:

```bash
cd twenty-crm-invoq-deploy
cp .env.example .env
nano .env
```

| Setting | What to put |
|---|---|
| `CRM_HOST` | The server's name from step 1 (for example `crm.34-18-187-167.sslip.io`) |
| `TAG` | `v2.59.2` (the Twenty version this guide was tested with) |
| `PG_DATABASE_PASSWORD` | A new random value from `openssl rand -hex 24` (letters and digits only, because it goes inside a web-style address) |
| `APP_SECRET`, `ENCRYPTION_KEY` | Each a new random value from `openssl rand -base64 32`. Leave `FALLBACK_ENCRYPTION_KEY` empty |
| `IS_SIGN_UP_DISABLED` | Set to `false` **for now** (it lets you create the first account) |

Keep `.env` private: it holds the passwords. Save a copy of it somewhere safe (a password manager).

**4B.2 Start the CRM:**

```bash
docker compose --env-file .env up -d
docker compose --env-file .env ps
```

Wait until `server` shows **(healthy)**: about 2 minutes on the first start.

**4B.3 Create the first Admin account.** Open `https://<CRM_HOST>` in a browser, choose **Continue with Email**,
sign up, and name the workspace **Topaztel**.

**4B.4 Close public sign-up again** (important: otherwise anyone could create an account). In `.env` change the
line to `IS_SIGN_UP_DISABLED=true`, then:

```bash
docker compose --env-file .env up -d server
```

**4B.5 Make an API key for the build.** In the CRM: Settings → **APIs & Webhooks** → **+ Create API key**, name
`build`, role **Admin**, expiry **1 day**. Copy the key and save it in a file without showing it on screen. On a Mac:
`pbpaste > ~/aroosh-admin.key && chmod 600 ~/aroosh-admin.key`. Never paste a key into a chat or a document.

**4B.6 Build everything from the documents** (run on any computer with Python 3, for example the same Mac):

```bash
TWENTY_URL=https://<CRM_HOST> KEY_FILE=~/aroosh-admin.key python3 scripts/build_from_docs.py
```

It prints each object and field it creates, then the record counts: `people: 7`, `tickets: 14`, `notes: 2`,
`catalog entries: 20`, `service requests: 4`, `interactions: 12`, and the roles Agent and Supervisor.
Running it twice is safe: it skips what already exists.

**4B.7 Delete the build key** when finished: Settings → APIs & Webhooks → the `build` key → Delete.

---

## Step 5. Check that it works

1. Open `https://<CRM_HOST>`: the page shows a padlock (HTTPS). The first visit can take one minute while the
   certificate is issued.
2. Log in. In the left menu you see **Tickets, Service Requests, Interactions, Catalog Entries**.
3. Search People for the phone number `501112222`: it finds **Fatima Khan** (loyalty ID LOY-1002).
4. The API answers. Without a key it refuses (this proves the address reaches the CRM):
   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' https://<CRM_HOST>/rest/tickets    # prints 403
   ```
   With a key (Settings → APIs & Webhooks):
   ```bash
   curl -s -H "Authorization: Bearer <API_KEY>" "https://<CRM_HOST>/rest/serviceRequests?limit=1"
   ```
5. Invite the team: Settings → Members → **Invite by link** → copy the link and send it privately. After they join,
   set their roles (Settings → Members → the person → Permissions → Role) and switch Invite by link off again.

## Step 6. After deployment

- **Only one live copy.** When a new copy goes live, stop the old one (for example Aroosh's laptop copy), or both
  run the SLA automation and send double emails, and changes made in one never reach the other.
- **Backups**, upgrades, own domain, costs and problem-solving: [docs/OPERATIONS.md](docs/OPERATIONS.md).

## If something goes wrong

| What you see | What to do |
|---|---|
| `wrong passphrase or damaged file` (Way A) | Type the passphrase again; check the file was copied completely |
| `.env already exists` (Way A) | The server was already set up. For a failed first attempt: `FORCE=1 scripts/import-export.sh ...` |
| `server` never becomes healthy | `docker compose --env-file .env logs server --tail 50` shows why. The first start takes 2 to 3 minutes |
| Browser warns about the certificate | Wait a minute; check ports 80 and 443 are open and `CRM_HOST` points to this server |
| Sign-up page says sign-up is disabled (Way B) | `IS_SIGN_UP_DISABLED` is still `true`: set `false` for step 4B.3 only |
| API key refused after Way A | `APP_SECRET` is not the one from the export; run the import again with `FORCE=1` |
| Connected mailbox shows an error after Way A | `ENCRYPTION_KEY` differs, or the mailbox password changed: reconnect it in Settings → Accounts |
| `build_from_docs.py` stops with a 400 error | It prints Twenty's message. Usually a field already exists with another type; tell Rishi |
